# Share Store
## Description
Share Store is a web-based file sharing and storage application built using Django and Python for the backend, and JavaScript and Bootstrap for the frontend. It is the final project for CS50's Web Programming with Python and JavaScript. This project contains a single app 'drive'.

Share Store allows users to register, log in, upload files, and manage access permissions for those files. Users can share their files with specific individuals or make them accessible to everyone. Additionally, users can view files shared with them by others. Share Store employs Firebase Storage for file storage and retrieval. It provides features like user authentication, file upload/download, and access control, making it a versatile file-sharing platform.

[Project Demo](https://youtu.be/0iN3-Odnxy0?si=5VipCIYMWm4CGpjJ)

## Updates
- **Discord Integration:** Enhanced the platform with a new feature that automates the process of uploading files `(college lecture slides in my case)` to Discord. Now, when users upload files containing specific keywords (e.g., lecture names or topics like Math or TOC) from their accounts, these files are automatically sent to a designated Discord channel, as specified in the environment variables. This integration eliminates the need for manual file transfers, saving time and ensuring that the content is promptly shared with the relevant Discord community.

**Screenshots**

> [!NOTE]
> The screenshot below demonstrates the Discord integration feature, specifically how the bot posts files to a designated thread/channel on your Discord server. This functionality is triggered by the `CHANNEL_MAPPINGS` configuration, such as including `"Maths": "maths thread/channel ID"` to direct math-related files to the appropriate Discord location.
>
> Project demo video is a bit old, so it does not showcase this feature.

<section style="text-align:center" align="center">
    <img src='screenshots/dev-wizard-automated-upload.jpg?raw=true' alt='Files posted/uploaded by a discord bot to a specific thread/channel.' width='250px' />
</section>

### Distinctiveness and Complexity
1. **Distinctiveness**:
    - **Unique Purpose**: Share Store specializes in secure file sharing and storage, setting it apart from traditional social networks or e-commerce sites.
    - **Targeted File Sharing**: Its main focus is on organized file sharing, not social interactions or product sales. The recent addition of Discord integration for file (automatic lecture slide) uploads further enhances its role as a specialized platform for content sharing.
    - **Firebase Integration**: Share Store integrates with Firebase Storage, enhancing file management.
2. **Complexity**:
    - **Django Backend**: Utilizes Django for user authentication, file metadata, and access control.
    - **JavaScript and Bootstrap**: Employs JavaScript and Bootstrap for a responsive frontend.
    - **User Authentication**: Implements secure user registration and login.
    - **File Management**: Handles complex tasks like file uploads, downloads, and access permissions.

### What’s contained in files
1. **`static/drive`**: Contains JavaScript for handling access permissions, the application's logo, and a stylesheet for styling.

2. **`templates/drive`**: Contains HTML templates responsible for rendering web pages.

3. **`firebase.py`**: Initializes the Firebase Admin SDK and creates a reference to Firebase Storage.

4. **`models.py`**: Defines data models for the application, including `File`, `User`, and `Share`.

5. **`tests.py`**: Includes database tests for creating files, shares, and users.

6. **`urls.py`**: Defines URL patterns for the 'drive' app.

7. **`utils.py`**: Contains a utility function for iterating over files fetched from external URLs.

8. **`views.py`**: Houses view functions that handle HTTP requests and define how web pages are rendered.

9. **`discord_integration.py`**: Manages the automation of uploading files to a specified Discord channel based on certain criteria, utilizing the Discord API.

10. **`requirements.txt`**: Lists external Python packages and dependencies required for the project.


### How to run Share Store
[Note: A brief guide on how to create a Firebase project and find the JSON service account key file for this project is given at the end.](#setting-up-firebase-for-share-store)

1. **Create a Virtual Environment (Optional)**:
   If you prefer to work within a virtual environment (recommended for isolation), you can create and activate one. Navigate to your project directory and run the following commands:

   ```bash
   # Create a virtual environment
   python -m venv myenv

   # Activate the virtual environment (Windows)
   myenv\Scripts\activate

   # Activate the virtual environment (macOS/Linux)
   source myenv/bin/activate
   ```

2. **Install Requirements**:
    Make sure you have Python installed on your system.
    Navigate to your project directory and install the required Python packages listed in `requirements.txt`. You can do this using `pip`:
    ```
    pip install -r requirements.txt
    ```
3. **Create .env File**:
    Create a file named .env in your project directory.
    In the .env file, add the following lines, replacing placeholder values with your actual configuration details:
    ```
    STORAGE_BUCKET="Storage Bucket Name"
    GOOGLE_APPLICATION_CREDENTIALS="Path to your Firebase Admin SDK JSON credential file"
    SECRET_KEY="Your Django secret key"
    CONNECTION_STRING="Your database connection string (production only)"
    SERVER_ID="Your Discord Server ID"
    BOT_TOKEN="Your Discord Bot Token"
    CHANNEL_MAPPINGS={"substring_1": "Channel_ID_1", "substring_2": "Channel_ID_2"}
    P_USERNAME="Specific platform username whose files will be checked for Discord posting."
    ```
    Each of these variables serves a specific purpose in your application, such as connecting to databases, integrating with Discord, and configuring Firebase services.

> [!TIP]
> If you want to look for more substrings, just add the mapping in the `CHANNEL_MAPPINGS` environment variable like so: `CHANNEL_MAPPINGS={"substring_1": "Channel_ID_1", "substring_2": "Channel_ID_2", "additional_substring": "Additional_Channel_ID"}`.

> [!NOTE]
> You should obtain the Firebase Admin SDK JSON credential file from your Firebase project settings. If you haven't already created a Firebase project, you can do so here: [Firebase Console](https://console.firebase.google.com/)
>
> Additionally, for setting up and obtaining your Discord Bot Token, refer to the Discord Developer Portal. Detailed instructions for creating a bot and inviting it to your server can be found here: [Discord Developer Portal](https://discord.com/developers/docs/intro).

4. **Database Migrations**:
    Run the following commands to create and apply database migrations:
    ```
    python manage.py makemigrations
    ```
    ```
    python manage.py migrate
    ```
5. **Run the Server**:
    Finally, start the development server with the following command:
    ```
    python manage.py runserver
    ```
6. **Access the Application**:
    Open a web browser and navigate to `http://localhost:8000`` to access the Share Store application.

---
#### Setting Up Firebase for Share Store
1. **Create a Firebase Project**:
    - Go to the [Firebase Console](https://console.firebase.google.com/).
    - Click "Add project" to create a new project.
    - Follow the setup instructions, including choosing a project name and enabling Google Analytics if needed.
2. **Navigate to Project Settings**:
    - After creating the project, click the gear icon (settings) next to "Project Overview" in the left sidebar.
    - Select "Project settings" from the dropdown.
3. **Add an App to Your Project**:
    - After creating the project, click the gear icon (settings) next to "Project Overview" in the left sidebar.
    - Select "Project settings" from the dropdown.
4. **Generate JSON Service Account Key**:
    - In your Firebase project settings, go to the "Service accounts" tab.
    - Under "Firebase Admin SDK," click "Generate new private key."
    - Download the JSON key file containing your credentials.
5. **Use the JSON Key File**:
    - Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable in your Share Store's `.env` file to the path of the downloaded JSON key file.
