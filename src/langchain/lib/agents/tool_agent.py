from langchain_experimental.tools import PythonREPLTool
from langchain_community.tools.shell import ShellTool
from langchain_openai import ChatOpenAI
from ..tools.utils import get_custom_tools
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from tempfile import TemporaryDirectory

from langchain_community.agent_toolkits import FileManagementToolkit

MEMORY_KEY = 'chat_memory'


def get_file_management_tools():
    working_directory = TemporaryDirectory()
    toolkit = FileManagementToolkit(
        root_dir=str(working_directory.name),
        selected_tools=["read_file", "write_file", "list_directory"],

    )
    return toolkit.get_tools()


def create_tool_agent():
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=(
                'You are a helpful GIS agent/consultant.\n'
                'Everything response that is reliant upon whitespaces, newlines, etc., '
                'should be surrounded in triple quotes (```<content here>```) for use in pre-tags.'
            )),
            MessagesPlaceholder(variable_name=MEMORY_KEY),
            HumanMessagePromptTemplate.from_template('{input}'),
            MessagesPlaceholder(variable_name='agent_scratchpad')
        ]
    )
    tools = [PythonREPLTool(), ShellTool()] + [tool()
                                               for tool in get_custom_tools()]
    print(tools)
    memory = ConversationBufferWindowMemory(
        k=6, memory_key=MEMORY_KEY, return_messages=True, input_key='input', output_key='output')

    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0,
                     streaming=True)
    agent = create_openai_tools_agent(
        llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True, memory=memory
    )

    return agent_executor
