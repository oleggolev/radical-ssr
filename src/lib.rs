use askama::Template;
use chrono::Local;
use serde::{Deserialize, Serialize};
use worker::*;

/// TODO: impose and enforce a character limit on title and content.
/// TODO: add a secondary post details page and only show post preview
///       on the primary page.
/// TODO: split the POST route into PUT (for creating new posts) and
///       POST for editing existing posts.
/// TODO: add an `updated_at`` field to the `Post` structure.
/// TODO: enable Markdown to HTML conversion for title and content.

#[derive(Deserialize, Serialize, Default, Debug)]
pub struct Post {
    pub id: u32,
    pub title: String,
    pub content: String,
    pub created_at: Option<String>, // time string in edge-local time
}

#[derive(Template)]
#[template(path = "index.html")]
pub struct IndexTemplate<'a> {
    pub posts: &'a Vec<Post>,
}

#[derive(Template)]
#[template(path = "about.html")]
pub struct AboutTemplate {}

#[derive(Debug, Deserialize, Serialize)]
struct GenericResponse {
    status: u16,
    message: String,
}

pub fn generate_api_response(status: u16, message: String) -> Result<Response> {
    if status == 200 {
        Response::from_json(&GenericResponse { status, message })
    } else {
        Response::error(message, status)
    }
}

pub fn generate_html_response<T>(status: u16, template: T) -> Result<Response>
where
    T: Template,
{
    let body = template.render().unwrap();
    Ok(Response::from_html(body).unwrap().with_status(status))
}

/// To add or edit an existing post, set request body to the following:
/// JSON {
///     id: u32
///     title: String(POST_TITLE_CHAR_LIMIT),
///     content: String(POST_CONTENT_CHAR_LIMIT)
/// }
async fn create_post(mut req: Request, ctx: RouteContext<()>) -> Result<Response> {
    let kv = ctx.kv("SSR_BENCH")?;
    let mut post = req.json::<Post>().await?;
    let post_id = post.id.to_string();
    post.created_at = Some(Local::now().format("%H:%M:%S %m-%d-%Y").to_string());
    kv.put(&post_id, post)?.execute().await?;
    generate_api_response(200, format!("Successfully added post #{post_id}"))
}

/// To delete an existing post, send an empty body with post id as URL parameter.
async fn delete_post(_req: Request, ctx: RouteContext<()>) -> Result<Response> {
    if let Some(id) = ctx.param("id") {
        let kv = ctx.kv("SSR_BENCH")?;
        kv.delete(id).await?;
        generate_api_response(200, format!("Successfully deleted post #{id}"))
    } else {
        generate_api_response(400, "Bad Request".to_string())
    }
}

/// Returns an HTML page with all posts.
async fn get_posts(_req: Request, ctx: RouteContext<()>) -> Result<Response> {
    let kv = ctx.kv("SSR_BENCH")?;
    let keys = kv.list().execute().await?.keys;
    let mut posts = Vec::with_capacity(keys.len());
    for key in keys {
        if let Some(res) = kv.get(&key.name).json::<Post>().await? {
            posts.push(res);
        }
        match kv.get(&key.name).json::<Post>().await {
            Ok(post) => {
                if let Some(post) = post {
                    posts.push(post)
                }
            }
            // If the value is not a Post, ignore it.
            Err(err) => match err {
                kv::KvError::Serialization(_) => continue,
                _ => Err(err)?,
            },
        }
    }
    let template = IndexTemplate { posts: &posts };
    generate_html_response(200, template)
}

/// Returns an HTML page with a simple About page.
async fn get_about(_req: Request, _ctx: RouteContext<()>) -> Result<Response> {
    let template = AboutTemplate {};
    generate_html_response(200, template)
}

#[event(fetch)]
async fn main(req: Request, env: Env, ctx: Context) -> Result<Response> {
    let router = Router::new();
    router
        .post_async("/post", create_post)
        .delete_async("/post/:id", delete_post)
        .get_async("/", get_posts)
        .get_async("/posts", get_posts)
        .get_async("/about", get_about)
        .run(req, env)
        .await
}
