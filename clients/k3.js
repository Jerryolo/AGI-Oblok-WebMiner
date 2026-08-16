export class K3Client {
  constructor({baseUrl, apiKey = "", model = "kimi-k3"}) { Object.assign(this, {baseUrl, apiKey, model}); }
  async chat({messages, tools, tool_choice, json_schema, partial_mode = false}) {
    const body = {model: this.model, messages, stream: partial_mode};
    if (tools) body.tools = tools;
    if (tool_choice) body.tool_choice = tool_choice;
    if (json_schema) body.response_format = {type: "json_schema", json_schema};
    const response = await fetch(`${this.baseUrl.replace(/\/$/, "")}/chat/completions`, {
      method: "POST", headers: {"Content-Type": "application/json", ...(this.apiKey && {Authorization: `Bearer ${this.apiKey}`})},
      body: JSON.stringify(body)
    });
    if (!response.ok) throw new Error(`K3 HTTP ${response.status}`);
    return partial_mode ? response.body : response.json();
  }
}
