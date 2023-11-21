use askama::Template;
use serde::{Deserialize, Serialize};
use worker::*;

#[derive(Deserialize, Serialize)]
pub struct Note {
    pub id: i32,
    pub title: String,
    // the note content can be rendered to markdown. See the source for more details
    pub markdown: String,
    pub update_at: Option<String>,
    pub created_at: String,
}

impl Default for Note {
    fn default() -> Note {
        Note {
            id: 12345,
            title: "hello".to_string(),
            markdown: "text".to_string(),
            update_at: None,
            created_at: "sometime".to_string(),
        }
    }
}

#[derive(Template)]
#[template(path = "index.html")]
pub struct IndexTemplate<'a> {
    pub notes: &'a Vec<Note>,
}

#[event(fetch)]
async fn main(req: Request, env: Env, ctx: Context) -> Result<Response> {
    let notes = vec![Note::default(), Note::default()];
    let notes_template_model = IndexTemplate { notes: &notes };
    let body = notes_template_model.render().unwrap();
    Ok(Response::from_html(body).unwrap().with_status(200))
}
