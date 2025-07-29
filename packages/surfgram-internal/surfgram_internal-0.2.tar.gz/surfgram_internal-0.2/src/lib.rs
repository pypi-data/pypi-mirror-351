use pyo3::{exceptions::PyIOError, prelude::*};
use pyo3_asyncio::tokio::future_into_py;
use reqwest::Client;

#[pyclass]
struct NativeClient {
    client: Client,
    base_url: String,
}

#[pymethods]
impl NativeClient {
    #[new]
    fn new(token: String) -> Self {
        let client = Client::builder()
            .tcp_nodelay(true)
            .pool_idle_timeout(None)
            .build()
            .unwrap();
            
        Self {
            client,
            base_url: format!("https://api.telegram.org/bot{}/", token),
        }
    }

    fn send_request<'py>(
        &self,
        py: Python<'py>,
        method: String,
        params: String,
    ) -> PyResult<&'py PyAny> {
        let client = self.client.clone();
        let url = format!("{}{}", self.base_url, method);
        
        future_into_py(py, async move {
            client.post(&url)
                .body(params)
                .header("Content-Type", "application/json")
                .send()
                .await
                .map_err(|e| PyIOError::new_err(e.to_string()))?
                .text()
                .await
                .map_err(|e| PyIOError::new_err(e.to_string()))
        })
    }
}

#[pymodule]
fn surfgram_internal(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<NativeClient>()?;
    Ok(())
}