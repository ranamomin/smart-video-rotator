# Smart Video Rotator

## Project Description

The Smart Video Rotator is a Python-based desktop application with a graphical user interface (GUI) that automatically corrects the orientation of videos. It uses a deep learning model to analyze the posture and alignment of a person within the video frames. By detecting the person's body axis and head position, the application intelligently determines the correct rotation needed to produce a video that is always upright and in the intended orientation (e.g., portrait).

The GUI, built with tkinter, provides a simple way to select an input folder, displays a progress bar, and shows real-time status updates as each video is analyzed and processed.

## How to Use the Software

### 1\. Prerequisites

Ensure you have the following installed on your system:

*   Python 3.x
    
*   pip (Python's package installer)
    
*   FFmpeg: This is a critical dependency for video rotation. You must have FFmpeg installed and configured in your system's PATH.
    

### 2\. Setup and Installation

It's highly recommended to use a Python virtual environment to manage project dependencies.

1.  Create a virtual environment:  
    python -m venv venv  
      
    
2.  Activate the virtual environment:
    

*   On Windows:  
    venv\\Scripts\\activate  
      
    
*   On macOS and Linux:  
    source venv/bin/activate  
      
    

3.  Install dependencies:  
    pip install -r requirements.txt  
      
    

### 3\. Running the Application

Once the dependencies are installed, you can run the GUI application from your terminal:

python gui.py  
  

The GUI will appear, and you can select a folder containing your videos to begin the process. The corrected videos will be saved in a new folder named corrected inside your input directory.

## How to Build the Executable (.exe)

For easy distribution, you can create a standalone executable using PyInstaller. This bundles the application and its dependencies into a single file.

### 1\. Install PyInstaller

If you haven't already, install PyInstaller in your virtual environment:

pip install pyinstaller  
  

### 2\. Build the Executable

Navigate to your project's root directory in your terminal and run the following command:

pyinstaller --noconsole --onefile --name "smart\_video\_rotator" gui.py  
  

*   \--noconsole: Prevents a command prompt window from appearing.
    
*   \--onefile: Packages the entire application into a single executable file.
    
*   \--name "smart\_video\_rotator": Sets the name of the output file to smart\_video\_rotator.exe.
    
*   gui.py: The entry point script for your application.
    

### 3\. Locating the Executable

After the command completes, you will find the smart\_video\_rotator.exe file in the dist/ folder of your project directory.
