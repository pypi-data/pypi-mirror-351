
from universal_mcp.servers import SingleMCPServer
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.stores import EnvironmentStore

from universal_mcp_notion.app import NotionApp

env_store = EnvironmentStore()
integration_instance = AgentRIntegration(name="notion", store=env_store)
app_instance = NotionApp(integration=integration_instance)

mcp = SingleMCPServer(
    app_instance=app_instance,
)

if __name__ == "__main__":
    mcp.run()


