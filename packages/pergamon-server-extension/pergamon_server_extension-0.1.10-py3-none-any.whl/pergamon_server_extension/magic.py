import json
import requests
import shlex
import os
from IPython.core.magic import Magics, magics_class, line_cell_magic
from IPython.display import display, HTML, Markdown
import plotly.graph_objects as go
from ipykernel.comm import Comm


# Global flag to track if the magic has been loaded
__MAGIC_LOADED__ = False

# Get API host from environment variable with default fallback
API_HOST = os.environ.get("CALLIOPE_API_HOST")

@magics_class
class CalliopeMagics(Magics):
    def __init__(self, shell):
        super(CalliopeMagics, self).__init__(shell)
        self.endpoint_map = {
            "sql_ask": "/api/sql/ask",
            "generate_sql": "/api/sql/generate_sql",
            "run_sql": "/api/sql/run_sql",
            "followup_questions": "/api/sql/generate_followup_questions",
            "generate_summary": "/api/sql/generate_summary",
            "rag_train": "/api/rag/train",
            "update_schema": "/api/rag/update_schema/{}",
            "clear_rag": "/api/rag/clear",
        }
        
        # Define available AI models and providers
        self.providers = {
            "ai21": {
                "name": "AI21",
                "models": ["j1-large", "j1-grande", "j1-jumbo", "j1-grande-instruct", 
                           "j2-large", "j2-grande", "j2-jumbo", "j2-grande-instruct", "j2-jumbo-instruct"]
            },
            "bedrock": {
                "name": "Amazon Bedrock",
                "models": ["amazon.titan-text-express-v1", "amazon.titan-text-lite-v1", "amazon.titan-text-premier-v1:0",
                           "ai21.j2-ultra-v1", "ai21.j2-mid-v1", "ai21.jamba-instruct-v1:0",
                           "cohere.command-light-text-v14", "cohere.command-text-v14", "cohere.command-r-v1:0", "cohere.command-r-plus-v1:0",
                           "meta.llama2-13b-chat-v1", "meta.llama2-70b-chat-v1", "meta.llama3-8b-instruct-v1:0", "meta.llama3-70b-instruct-v1:0",
                           "meta.llama3-1-8b-instruct-v1:0", "meta.llama3-1-70b-instruct-v1:0", "meta.llama3-1-405b-instruct-v1:0",
                           "mistral.mistral-7b-instruct-v0:2", "mistral.mixtral-8x7b-instruct-v0:1", "mistral.mistral-large-2402-v1:0", "mistral.mistral-large-2407-v1:0"]
            },
            "bedrock-chat": {
                "name": "Amazon Bedrock Chat",
                "models": ["amazon.titan-text-express-v1", "amazon.titan-text-lite-v1", "amazon.titan-text-premier-v1:0",
                           "anthropic.claude-v2", "anthropic.claude-v2:1", "anthropic.claude-instant-v1",
                           "anthropic.claude-3-sonnet-20240229-v1:0", "anthropic.claude-3-haiku-20240307-v1:0", "anthropic.claude-3-opus-20240229-v1:0",
                           "anthropic.claude-3-5-haiku-20241022-v1:0", "anthropic.claude-3-5-sonnet-20240620-v1:0", "anthropic.claude-3-5-sonnet-20241022-v2:0",
                           "meta.llama2-13b-chat-v1", "meta.llama2-70b-chat-v1", "meta.llama3-8b-instruct-v1:0", "meta.llama3-70b-instruct-v1:0",
                           "meta.llama3-1-8b-instruct-v1:0", "meta.llama3-1-70b-instruct-v1:0", "meta.llama3-1-405b-instruct-v1:0",
                           "mistral.mistral-7b-instruct-v0:2", "mistral.mixtral-8x7b-instruct-v0:1", "mistral.mistral-large-2402-v1:0", "mistral.mistral-large-2407-v1:0"]
            },
            "bedrock-custom": {
                "name": "Amazon Bedrock Custom",
                "help": "For Cross-Region Inference use the appropriate Inference profile ID (Model ID with a region prefix, e.g., us.meta.llama3-2-11b-instruct-v1:0). For custom/provisioned models, specify the model ARN (Amazon Resource Name) as the model ID."
            },
            "anthropic-chat": {
                "name": "Anthropic",
                "models": ["claude-2.0", "claude-2.1", "claude-3-opus-20240229", "claude-3-sonnet-20240229", 
                           "claude-3-haiku-20240307", "claude-3-5-haiku-20241022", "claude-3-5-sonnet-20240620", "claude-3-5-sonnet-20241022"]
            },
            "azure-chat-openai": {
                "name": "Azure OpenAI",
                "help": "This provider does not define a list of models."
            },
            "cohere": {
                "name": "Cohere",
                "models": ["command", "command-nightly", "command-light", "command-light-nightly", 
                           "command-r-plus", "command-r"]
            },
            "gemini": {
                "name": "Google Gemini",
                "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro", "gemini-1.0-pro-001", 
                           "gemini-1.0-pro-latest", "gemini-1.0-pro-vision-latest", "gemini-pro", "gemini-pro-vision"]
            },
            "gpt4all": {
                "name": "GPT4All",
                "models": ["ggml-gpt4all-j-v1.2-jazzy", "ggml-gpt4all-j-v1.3-groovy", "ggml-gpt4all-l13b-snoozy",
                           "mistral-7b-openorca.Q4_0", "mistral-7b-instruct-v0.1.Q4_0", "gpt4all-falcon-q4_0",
                           "wizardlm-13b-v1.2.Q4_0", "nous-hermes-llama2-13b.Q4_0", "gpt4all-13b-snoozy-q4_0",
                           "mpt-7b-chat-merges-q4_0", "orca-mini-3b-gguf2-q4_0", "starcoder-q4_0",
                           "rift-coder-v0-7b-q4_0", "em_german_mistral_v01.Q4_0"]
            },
            "huggingface_hub": {
                "name": "Hugging Face Hub",
                "help": "See https://huggingface.co/models for a list of models. Pass a model's repository ID as the model ID; for example, huggingface_hub:ExampleOwner/example-model."
            },
            "mistralai": {
                "name": "Mistral AI",
                "models": ["open-mistral-7b", "open-mixtral-8x7b", "open-mixtral-8x22b", "mistral-small-latest",
                           "mistral-medium-latest", "mistral-large-latest", "codestral-latest"]
            },
            "nvidia-chat": {
                "name": "NVIDIA AI",
                "models": ["playground_llama2_70b", "playground_nemotron_steerlm_8b", "playground_mistral_7b",
                           "playground_nv_llama2_rlhf_70b", "playground_llama2_13b", "playground_steerlm_llama_70b",
                           "playground_llama2_code_13b", "playground_yi_34b", "playground_mixtral_8x7b",
                           "playground_neva_22b", "playground_llama2_code_34b"]
            },
            "openai": {
                "name": "OpenAI",
                "models": ["babbage-002", "davinci-002", "gpt-3.5-turbo-instruct"]
            },
            "openai-chat": {
                "name": "OpenAI Chat",
                "models": ["gpt-3.5-turbo", "gpt-3.5-turbo-1106", "gpt-4", "gpt-4-turbo", "gpt-4-turbo-preview",
                           "gpt-4-0613", "gpt-4-0125-preview", "gpt-4-1106-preview", "gpt-4o", "gpt-4o-2024-11-20",
                           "gpt-4o-mini", "chatgpt-4o-latest"]
            },
            "openai-chat-custom": {
                "name": "OpenAI API Compatible",
                "help": "Supports non-OpenAI models that use the OpenAI API interface. Replace the OpenAI API key with the API key for the chosen provider."
            },
            "openrouter": {
                "name": "OpenRouter",
                "help": "This provider does not define a list of models."
            },
            "qianfan": {
                "name": "Qianfan",
                "models": ["ERNIE-Bot", "ERNIE-Bot-4"]
            },
            "sagemaker-endpoint": {
                "name": "SageMaker Endpoint",
                "help": "Specify an endpoint name as the model ID. In addition, you must specify a region name, request schema, and response path."
            },
            "togetherai": {
                "name": "Together AI",
                "models": ["Austism/chronos-hermes-13b", "DiscoResearch/DiscoLM-mixtral-8x7b-v2", "EleutherAI/llemma_7b",
                           "Gryphe/MythoMax-L2-13b", "Meta-Llama/Llama-Guard-7b", "Nexusflow/NexusRaven-V2-13B",
                           "NousResearch/Nous-Capybara-7B-V1p9", "NousResearch/Nous-Hermes-2-Yi-34B",
                           "NousResearch/Nous-Hermes-Llama2-13b", "NousResearch/Nous-Hermes-Llama2-70b"]
            }
        }
        
        # Define model aliases
        self.model_aliases = {
            "gpt2": "huggingface_hub:gpt2",
            "gpt3": "openai:davinci-002",
            "chatgpt": "openai-chat:gpt-3.5-turbo",
            "gpt4": "openai-chat:gpt-4",
            "openrouter-claude": "openrouter:anthropic/claude-3.5-sonnet:beta",
            "anthropic-chat": "anthropic-chat:claude-2.0",
            "native-cohere": "cohere:command",
            "bedrock-cohere": "bedrock:cohere.command-text-v14",
            "anthropic": "anthropic:claude-v1",
            "bedrock": "bedrock:amazon.titan-text-lite-v1",
            "gemini": "gemini:gemini-1.0-pro-001",
            "gpto": "openai-chat:gpt-4o"
        }
        
    @line_cell_magic
    def calliope(self, line, cell=None):
        args = shlex.split(line) if line else []
        
        if not args:
            return self._handle_help()

        action = args[0].lower()
        match action:
            case "help":
                return self._handle_help()
            case "list_models":
                return self._handle_list_models(args[1:] if len(args) > 1 else [])
            case "ask":
                if self._validate_has_content(cell):
                    return self._validate_has_content(cell)
                return self._handle_ask(args[1:], cell)
            case _:
                if self._validate_has_content(cell):
                    return self._validate_has_content(cell)

                
                # Process remaining arguments
                remaining_args = args[1:]
                datasource_id = ""
                to_ai = False
                ai_model = "gpto"
                
                i = 0
                while i < len(remaining_args):
                    if i == 0 and remaining_args[i] not in ["--to-ai", "--model"]:
                        datasource_id = remaining_args[i]
                    elif remaining_args[i] == "--to-ai":
                        to_ai = True
                    elif remaining_args[i] == "--model" and i + 1 < len(remaining_args):
                        ai_model = remaining_args[i + 1]
                        i += 1
                    i += 1
                    
                # Handle API commands
                return self._handle_api_command(action, datasource_id, cell, to_ai, ai_model)
    
    def _handle_list_models(self, args):
        """Handle the list_models command to display available AI models"""
        # provider_filter = args[0] if args else None
        
        # markdown_output = self._format_models_markdown(provider_filter)
        # display(Markdown(markdown_output))
        self.shell.run_cell('%ai list')
        return None
    
    def _format_models_markdown(self, provider_filter=None):
        """Format the available models as markdown"""
        output = "# Available AI Models\n\n"
        output += "| Provider | Models |\n"
        output += "|----------|--------|\n"
        
        for provider_id, provider_info in self.providers.items():
            if provider_filter and provider_filter != provider_id:
                continue
                
            # Format the models list
            if "help" in provider_info:
                models_list = f"<p>{provider_info['help']}</p>"
            elif "models" in provider_info:
                models_list = "<ul>"
                for model in provider_info.get("models", []):
                    full_model_id = f"{provider_id}:{model}"
                    models_list += f"<li><code>{full_model_id}</code></li>"
                models_list += "</ul>"
            else:
                models_list = "<p>No models defined</p>"
            
            output += f"| **{provider_info.get('name')}** | {models_list} |\n"
        
        # Add model aliases section
        if not provider_filter and self.model_aliases:
            output += "\n## Model Aliases\n\n"
            output += "| Alias | Maps to |\n"
            output += "|-------|--------|\n"
            
            for alias, target in self.model_aliases.items():
                output += f"| `{alias}` | `{target}` |\n"
                
        return output

    def _validate_has_content(self, cell):
        """Validate that the cell has content"""
        if not cell or not cell.strip():
            return {"error": "Empty content provided"}
        return None

    def _handle_help(self):
        """Handle the help command"""
        help_text = """# Calliope Magic Commands

## Basic Usage
```
%%calliope [action] [datasource_id] [options]
your content here
```

## Available Actions

### Data Querying & Analysis
- `sql_ask`: Ask natural language questions about your data and get AI-generated SQL, results, summary, visualization, and followup questions
- `generate_sql`: Convert a natural language question to SQL without executing it
- `run_sql`: Execute a SQL query directly on your datasource
- `followup_questions`: Generate contextual follow-up questions based on previous query results
- `generate_summary`: Create a concise summary of query results

### RAG System Management
- `rag_train`: Train the RAG system with custom data (DDL, documentation, or example question/SQL pairs)
- `update_schema`: Update the schema definition for a specific datasource
- `clear_rag`: Clear all RAG data in the system

### Other Commands
- `ask`: Direct AI query for general assistance and explanations
- `help`: Display this help message
- `list_models`: Display available AI models and their status

## Options
- `--to-ai`: Process API results through an AI model for enhanced explanation
- `--model [model_name]`: Specify which AI model to use (default: gpto)

## Detailed Examples

### sql_ask
Translates natural language to SQL, executes it, and returns results with summary, visualization, and follow-up suggestions.

```
%%calliope sql_ask sales_db
What were our top 5 selling products last quarter by revenue?
```

Output includes:
- Natural language summary of results
- Visualization of the data (when appropriate)
- The executed SQL query
- Suggested follow-up questions

### generate_sql
Translates a natural language question to SQL without executing it.

```
%%calliope generate_sql customer_db
Find all customers who made more than 3 purchases in the last 30 days
```

### run_sql
Directly executes SQL on your datasource.

```
%%calliope run_sql inventory_db
SELECT 
    product_name, 
    stock_level, 
    reorder_point,
    CASE WHEN stock_level < reorder_point THEN 'Reorder' ELSE 'OK' END AS status
FROM inventory
WHERE category = 'Electronics'
ORDER BY stock_level ASC;
```

### followup_questions
Generate follow-up questions based on previous query results. Requires JSON input with previous context.

```
%%calliope followup_questions
{
    "question": "How many orders were placed last month?",
    "sql_query": "SELECT COUNT(*) as order_count FROM orders WHERE order_date >= '2023-04-01' AND order_date < '2023-05-01'",
    "results": "[{\"order_count\": 1354}]"
}
```

### generate_summary
Create a human-readable summary of query results.

```
%%calliope generate_summary financial_db
[{"month": "January", "revenue": 125000}, {"month": "February", "revenue": 118000}, {"month": "March", "revenue": 142000}]
```

### rag_train
Train the RAG system with custom data in three possible formats:
1. DDL statements to define schema
2. Documentation about tables, columns, and relationships
3. Example question/SQL pairs for few-shot learning

```
%%calliope rag_train customer_db
{
    "ddl": [
        "CREATE TABLE customers (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), signup_date DATE)",
        "CREATE TABLE orders (id INT PRIMARY KEY, customer_id INT, order_date DATE, total_amount DECIMAL(10,2))"
    ]
}
```

Or with documentation:

```
%%calliope rag_train customer_db
{
    "documentation": [
        "The customers table contains all registered users with their basic information",
        "The signup_date field represents when the customer first created their account",
        "The orders table tracks all purchases with a foreign key to customers"
    ]
}
```

Or with example pairs:

```
%%calliope rag_train customer_db
{
    "question": [
        "How many customers signed up last month?", 
        "What is our average order value?"
    ],
    "sql": [
        "SELECT COUNT(*) FROM customers WHERE signup_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') AND signup_date < DATE_TRUNC('month', CURRENT_DATE)",
        "SELECT AVG(total_amount) FROM orders"
    ]
}
```

### update_schema
Update the schema definition for a specific datasource.

```
%%calliope update_schema product_db
```

### clear_rag
Clear all RAG training data from the system.

```
%%calliope clear_rag
```

### ask
Access Calliope's AI capabilities for general questions, explanations, and assistance with data concepts.

```
%%calliope ask gpt4
Explain the difference between INNER JOIN and LEFT JOIN in SQL
```

You can specify different AI models:
```
%%calliope ask claude3
What are best practices for designing efficient database schemas?
```

### list_models
Display all available AI models and their status.

```
%calliope list_models
```

Or filter by provider:
```
%calliope list_models openai
```

### Using AI Processing
Add the `--to-ai` flag to process results with an AI model for enhanced explanation:

```
%%calliope sql_ask financial_db --to-ai
What was our profit margin trend over the last 4 quarters?
```

Specify a different AI model with `--model`:

```
%%calliope sql_ask user_db --to-ai --model claude3
Which user segments have the highest retention rates?
```"""
        display(Markdown(help_text))
        return None
        
    def _handle_ask(self, args, cell):
        """Handle the ask command (proxy to %%ai)"""
        ai_args = " ".join(args) if args else ""
        ai_magic = f"%%ai {ai_args}\n{cell or ''}"
        self.shell.run_cell(ai_magic)
        return None

    def _handle_api_command(self, action, datasource_id, cell, to_ai, ai_model):
        """Handle commands that use the API"""
        try:
            if action not in self.endpoint_map:
                valid_actions = ", ".join(f"'{a}'" for a in self.endpoint_map.keys())
                return {"error": f"Invalid action: {action}. Must be one of: {valid_actions}"}
            
            if action in ["sql_ask", "generate_sql", "run_sql", "generate_summary", "rag_train", "update_schema"] and not datasource_id:
                return {"error": f"Missing datasource_id. Usage: %%calliope {action} [datasource_id]"}
            
            if action == "update_schema":
                endpoint = f"{API_HOST}{self.endpoint_map[action].format(datasource_id)}"
            else:
                endpoint = f"{API_HOST}{self.endpoint_map[action]}"
            
            payload = self._prepare_payload(action, datasource_id, cell)
            
            response = requests.post(
                endpoint,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=100
            )
            
            response.raise_for_status()
            
            try:
                result = response.json()    
                
                if to_ai:
                    return self._process_with_ai(result, cell, ai_model)
                else:
                    if action == "sql_ask":
                        self._display_formatted_result(result, action)
                        return None
                    return result
                
            except json.JSONDecodeError:
                return {"error": "API response was not valid JSON", "response_text": response.text[:200]}
                
        except requests.RequestException as e:
            error_msg = str(e)
            return {
                "error": "Failed to connect to API endpoint",
                "details": error_msg,
                "endpoint": endpoint
            }
        
    
    def _prepare_payload(self, action, datasource_id, cell):
        """Prepare the payload for the API request based on the action"""
        payload = {}
        
        match action:
            case "sql_ask":
                payload = {
                    "question": cell.strip(),
                    "datasource_id": datasource_id,
                    "generate_summary": True,
                    "generate_chart": True,
                    "generate_followups": True
                }
            case "generate_sql":
                payload = {
                    "question": cell.strip(),
                    "datasource_id": datasource_id
                }
            case "run_sql":
                payload = {
                    "sql_query": cell.strip(),
                    "datasource_id": datasource_id
                }
            case "followup_questions":
                try:
                    data = json.loads(cell.strip())
                    question = data.get("question")
                    sql_query = data.get("sql_query") 
                    results = data.get("results")
                    
                    if not all([question, sql_query, results]):
                        return {"error": "Cell must contain JSON with format: {'question': '...', 'sql_query': '...', 'results': '...'}"}
                        
                except json.JSONDecodeError:
                    return {"error": "Cell must contain valid JSON with format: {'question': '...', 'sql_query': '...', 'results': '...'}"} 
                payload = {
                    "question": question,
                    "sql_query": sql_query,
                    "results": results
                }
            case "generate_summary":
                payload = {
                    "query_results": cell.strip(),
                    "datasource_id": datasource_id
                }
            case "rag_train":
                try:
                    data = json.loads(cell.strip())
                    
                    if "ddl" in data and isinstance(data["ddl"], list) and all(isinstance(x, str) for x in data["ddl"]):
                        payload = {
                            "ddl": data["ddl"],
                            "datasource_id": datasource_id
                        }
                    elif "documentation" in data and isinstance(data["documentation"], list) and all(isinstance(x, str) for x in data["documentation"]):
                        payload = {
                            "documentation": data["documentation"],
                            "datasource_id": datasource_id
                        }
                    elif ("question" in data and isinstance(data["question"], list) and all(isinstance(x, str) for x in data["question"]) and
                        "sql" in data and isinstance(data["sql"], list) and all(isinstance(x, str) for x in data["sql"])):
                        payload = {
                            "question": data["question"],
                            "sql": data["sql"],
                            "datasource_id": datasource_id
                        }
                    else:
                        return {"error": "Payload must contain either ddl: string[], documentation: string[], or both question: string[] and sql: string[]"}
                except json.JSONDecodeError:
                    return {"error": "Cell must contain valid JSON"}
            case "update_schema":
                pass
            case "clear_rag":
                pass
                
        return payload
    
    def _process_with_ai(self, result, cell, ai_model):
        """Process the API result with AI"""
        ai_prompt = f"""\
        Please interpret this response in the context of the question: {cell.strip()}. 
        Format the response strictly as a Jupyter notebook response with the appropriate markdown.

        ---BEGIN DATA---
        Summary: {result.get("summary")}
        Response: {result.get("response")}
        Followup Questions: {", ".join(result.get("followup_questions", []))}
        SQL Query: {result.get("sql_query")}
        ---END DATA---
        """

        ai_magic = f"%%ai {ai_model} --format code\n{ai_prompt}"
        self.shell.run_cell(ai_magic)
        return None
    
    def _display_formatted_result(self, result, action):
        """Format and display the result with proper markdown and visualizations"""
        if "error" in result:
            display(HTML(f"<div style='color: red; font-weight: bold;'>Error: {result['error']}</div>"))
            if "details" in result:
                display(HTML(f"<div style='color: red;'>Details: {result['details']}</div>"))
            return
        
        markdown_output = ""
        
        if "datasource_id" in result and result["datasource_id"]:
            markdown_output += f"## Query Results: {result.get('datasource_id', '')}\n\n"
        
        if "summary" in result and result["summary"]:
            markdown_output += f"### Summary\n{result['summary']}\n\n"
        
        if "response" in result and result["response"]:
            markdown_output += f"{result['response']}\n\n"
        
        if "visualization" in result and result["visualization"]:
            display(Markdown(markdown_output))
            
            try:
                visualization = result["visualization"]
                fig = go.Figure(
                    data=visualization.get("data", []),
                    layout=visualization.get("layout", {})
                )
                
                fig.show()
                
                markdown_output = ""
            except Exception as e:
                markdown_output += f"**Error displaying visualization:** {str(e)}\n\n"
        
        if "sql_query" in result and result["sql_query"]:
            markdown_output += f"### Executed SQL\n```sql\n{result['sql_query']}\n```\n\n"
        
        if "followup_questions" in result and result["followup_questions"]:
            markdown_output += "### Suggested Follow-up Questions\n"
            for question in result["followup_questions"]:
                markdown_output += f"- {question}\n"
            markdown_output += "\n"
        
        if markdown_output:
            display(Markdown(markdown_output))

def load_ipython_extension(ipython):
    """
    Register the magic with IPython.
    This function is called when the extension is loaded.
    
    Can be manually loaded in a notebook with:
    %load_ext pergamon_server_extension
    """
    global __MAGIC_LOADED__
    
    if not __MAGIC_LOADED__:
        ipython.register_magics(CalliopeMagics)
        __MAGIC_LOADED__ = True
    else:
        pass

load_ext = load_ipython_extension 

