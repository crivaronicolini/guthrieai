# Setup instructions
Install Ollama following the [website instructions](https://ollama.com/download). Prefer the manual install for your OS. On linux it is:
```sh
curl -fsSL https://ollama.com/download/ollama-linux-amd64.tgz \
    | sudo tar zx -C /usr
```

Install the gemma3 model and serve it using the 0.0.0.0 host. This will make the url accessible to the Docker container. Alternatively, follow [these instructions](https://github.com/ollama/ollama/issues/703#issuecomment-1951444576) to configure the Ollama service.
```sh
ollama pull gemma3

OLLAMA_HOST="0.0.0.0:11434" ollama serve
```

The Llama 3 model is also available in the app. To use it, pull the model with the same command as above.

# Running the app
Clone the repo and run:
```sh
git clone git@github.com:crivaronicolini/guthrieai.git
cd guthrieai
cp env.example .env
docker compose up --build
```

The app runs on [http://127.0.0.1:5000](http://127.0.0.1:5000).

# To Do
- Dialog for updating each model configuration (system prompt, name).
- Making each bot have a distinct color, also configurable.
- Token streaming support.
- Generated conversation titles.
- Message queueing

