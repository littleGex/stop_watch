# Stopwatch
Track time on projects

Programming language:
Python 3.7 and pyqt5

Set environment:
XYZ

Start GUI:
python timing.py or using spyder

Document location:
The program creates a 'Timer' folder in C:/Users/<USERid>/Documents/ folder.  Saving and restoring sessions, saving csv and pdf all direct to this folder in the first instance.

When starting the GUI the user will be asked if they wish to restore a previous session to continue tracking.  If no is selected a blank session is shown including the default 'Project A' in the list of projects.

Using the timer:
Using 'START', 'PAUSE' and 'STOP' the user opperates the stop watch feature - The timer can be reset using 'RESET'.

The drop-down box updates to show the project names shown in the table view.  To commit the time to a specific project, if the project already exists, simply select the project in the drop-down list and press 'COMMIT'.  The time will then be appended to the project.

If the project does not exist, use the text field below the table to record the project name and press 'ADD ROW', the drop-down will be updated and then the time can be added to that project.

Presenting results:
The 'Timer' tab shows the total time spent on the project in table form with a graphical representation shown on the 'Graphic' tab (subject to improvement).
Graphic is automatically updated when data is commited to the table - see 'Using the timer'.

Additionally the table can be exported using the keyboard shortcut "ctrl+C" and the graph exported as PDF using "ctrl+P" or using the file menu options.  The table data export as csv can also be started using the 'EXPORT' button.

Sessions:
The default session shows a table with 'Project A' in the table.
A new session can be started using "ctrl+N" or using the file menu.
The session can be saved using "ctrl+S" and restored using "ctrl+R" or using Session file menu.
Upon quiting ("ctrl+Q"), the user is asked whether they wish to save the session - it is not automatically saved, but this could be a default solution in a newer version.  
