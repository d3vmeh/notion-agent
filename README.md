# Notion Task Manager Agent

A comprehensive Python-based task management AI agent that integrates with Notion to create, query, update, and manage tasks using natural language input. Supports both speech and text input with intelligent LLM-powered parsing and management.

## 🚀 Features

### Core Functionality
- **🎤 Speech Input**: Add and manage tasks using voice commands with automatic audio transcription
- **⌨️ Text Input**: Type your requests directly
- **🤖 AI-Powered Intent Classification**: Automatically determines what you want to do (create, query, update, delete, search)
- **📋 Task Creation**: Add single or multiple tasks with intelligent parsing
- **🔍 Task Querying**: View and filter tasks with natural language queries
- **🔄 Task Updating**: Modify existing tasks using natural language


### Smart Features
- **📅 Intelligent Date Parsing**: Converts natural language dates to proper format with timezone support
- **🏷️ Automatic Categorization**: Categorizes tasks (General, Personal, Fitness, Fun, School)
- **⚡ Priority Management**: Supports Low, Medium, and High priority levels
- **📝 Rich Notes**: Add detailed notes and descriptions to tasks

## 📋 Task Structure

Each task includes:
- **Task Name**: The title/name of the task
- **Due Date**: Date and time in YYYY-MM-DD HH:MM format
- **Priority**: Low, Medium, or High
- **Category**: General, Personal, Fitness, Fun, or School
- **Status**: To-Do, In Progress, or Completed
- **Notes**: Additional details and context

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- A Notion account with a database
- OpenAI API key

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd notion-agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   # Create a .env file or set environment variables
   export OPENAI_API_KEY="your-openai-api-key"
   export NOTION_TOKEN="your-notion-integration-token"
   export NOTION_DATABASE_URL="https://notion.so/workspace/your-database-id?v=..."
   ```

4. **Configure Notion**:
   - Create a Notion integration at https://www.notion.so/my-integrations
   - Share your database with the integration
   - Copy the full database URL (the system will automatically extract the database ID)

## 🎯 Usage

### Starting the Agent

```bash
python notion_manager_agent.py
```

### Input Methods

#### 1. 🎤 Speech Input
- Press **ENTER** to start recording
- **Speak your request** clearly
- **Pause for 5 seconds** when you're done (or continue speaking naturally)
- View the transcription and confirm

#### 2. ⌨️ Text Input
- Type your request directly
- Press **ENTER** to submit

## 💬 Command Examples

### Task Creation
```
"Add a meeting with John tomorrow at 2pm to discuss the new project requirements"
"High priority workout session - need to focus on cardio and strength training"
"Add three tasks: workout tomorrow at 6am, buy groceries today at 5pm, and call mom on Friday at 3pm"
```

### Task Querying
```
"Show me all my tasks for this week"
"What tasks do I have today?"
"Show me high priority tasks"
"Display tasks in the Fitness category"
"Show me completed tasks from last month"
```

### Task Updating
```
"Mark the workout task as completed"
"Change the meeting time to 3pm tomorrow"
"Update the project task to high priority"
"Change the grocery shopping category to Personal"
"Add notes about the deadline to the project task"
"Change the status of the presentation task to In Progress"
```

## 🔧 How It Works

### Intent Classification
The agent uses GPT-4 to automatically classify your intent:
- **CREATE_TASK**: Adding new tasks
- **QUERY_TASKS**: Viewing and filtering tasks
- **UPDATE_TASK**: Modifying existing tasks
- **DELETE_TASK**: Removing tasks (coming soon)
- **SEARCH_TASKS**: Finding specific tasks (coming soon)

### Task Creation Process
1. **Intent Detection**: Determines you want to create tasks
2. **Natural Language Parsing**: Uses LLM to extract task details
3. **Structured Output**: Converts to JSON format
4. **Notion Integration**: Adds tasks to your database

### Task Querying Process
1. **Intent Detection**: Determines you want to query tasks
2. **Query Parsing**: Extracts filters and sorting preferences
3. **Database Query**: Retrieves matching tasks from Notion
4. **AI Summary**: Generates natural language summary of results using an LLM

### Task Updating Process
1. **Intent Detection**: Determines you want to update a task
2. **Update Parsing**: Extracts what task to update and what changes to make
3. **Task Identification**: Finds the specific task in your database
4. **Update Execution**: Modifies the task in Notion
5. **Confirmation**: Shows updated task details

## 🔧 Configuration

### Speech Recognition Settings

The speech recognition can be configured in `speech_tools.py`:

```python
recognizer.energy_threshold = 100          # Microphone sensitivity
recognizer.pause_threshold = 5.0           # Seconds of silence before stopping
recognizer.non_speaking_duration = 2.0     # Seconds of silence to consider speech done
```

### Notion Database Structure

Your Notion database should have these properties:
- **Task** (Title): The task name
- **Due Date** (Date): When the task is due
- **Priority** (Select): Low, Medium, High
- **Category** (Select): General, Personal, Fitness, Fun, School
- **Status** (Select): To-Do, In Progress, Completed
- **Notes Page** (Text): Additional details

## 🧪 Testing

### Microphone Test

Run the microphone test to verify your audio setup:

```bash
python debug/test_microphone.py
```

This will:
- Check microphone accessibility
- List available microphones
- Test audio recording
- Test speech recognition
- Provide troubleshooting tips

## 🔍 Troubleshooting

### Speech Input Issues

1. **"No audio recorded"**:
   - Check microphone permissions
   - Ensure microphone is not muted
   - Run `debug/test_microphone.py` to verify setup

2. **Poor transcription quality**:
   - Speak clearly and at a normal pace
   - Reduce background noise
   - Check microphone volume

3. **Recording stops too quickly**:
   - Increase `pause_threshold` in `speech_tools.py`
   - Speak continuously or pause for shorter periods

### Notion Integration Issues

1. **"Error adding task to Notion"**:
   - Verify your Notion token is correct
   - Check database ID
   - Ensure integration has access to the database
   - Verify database property names match expected structure

2. **Database not found**:
   - Copy the correct database ID from the URL
   - Share the database with your integration


## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for GPT-4 API
- [Notion](https://notion.so/) for the database platform
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) for speech processing
- [Google Speech Recognition](https://cloud.google.com/speech-to-text) for transcription
