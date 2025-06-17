# Notion Task Agent

Python-based task management agent that allows you to add tasks to your Notion database using natural language input, with support for both speech and text input.

## 🚀 Features

- **🎤 Speech Input**: Add tasks using voice commands with automatic audio transcription
- **⌨️ Text Input**: Type your tasks directly
- **📋 Multiple Tasks**: Add multiple tasks at once in a single input
- **🤖 AI-Powered**: Uses GPT-4 to intelligently parse natural language into structured tasks
- **📅 Smart Date Parsing**: Automatically converts natural language dates to proper format with timezone support
- **🏷️ Task Categorization**: Automatically categorizes tasks (General, Personal, Fitness, Fun, School)
- **⚡ Priority Levels**: Supports Low, Medium, and High priority levels
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

- Python 3.7 or higher
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
python notion_agent.py
```

### Input Methods

#### 1. 🎤 Speech Input
- Press **ENTER** to start recording
- **Speak your task(s)** clearly
- **Pause for 5 seconds** when you're done (or continue speaking naturally)
- View the transcription and confirm

#### 2. ⌨️ Text Input
- Type your task description directly
- Press **ENTER** to submit

### Example Inputs

#### Single Tasks
```
"Add a meeting with John tomorrow at 2pm to discuss the new project requirements"
"High priority workout session - need to focus on cardio and strength training"
"Complete the math homework for school - chapters 5 and 6, due next week"
```

#### Multiple Tasks
```
"Add three tasks: workout tomorrow at 6am, buy groceries today at 5pm, and call mom on Friday at 3pm"
"I need to prepare for my presentation: research topic tomorrow, create slides on Wednesday, and practice on Thursday"
```

### Task Examples

The AI will automatically parse your input into structured tasks:

**Input**: "Add a meeting with John tomorrow at 2pm to discuss the new project requirements"

**Output**:
```json
{
  "task_name": "Meeting with John",
  "due_date": "2025-06-12 14:00",
  "priority": "Medium",
  "category": "General",
  "status": "To-Do",
  "notes": "Discuss new project requirements"
}
```

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
python test_microphone.py
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
   - Run `test_microphone.py` to verify setup

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
