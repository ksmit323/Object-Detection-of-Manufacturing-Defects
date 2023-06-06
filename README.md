# Introduction 
---
The repo contains all the code and other files to run the Polaris Neural Network.  

# Getting Started
---
1. ##Installation Process

    Copy and paste the following command in the terminal window of your local machine:
       
    ```
    git clone https://NorthstarPrecisionVietnam@dev.azure.com/NorthstarPrecisionVietnam/PolarisNNet/_git/PolarisNNet
    ```

    When prompted for a password, click on the "Repos" tab and click "Clone" button in the top left corner .  
    
    Click "Generate Git Credentials" and copy the 
    password. Paste it into the terminal window on your local machine. 

    You need to repeat this process exactly for the local_orch repo. 
    Go to the top of the page and click the orange icon where it says PolarisNNet / Repos / Files /... 
    
    Use this icon to switch between repos.  Below is the command for cloning the local_orch repo:

    ```
    git clone https://NorthstarPrecisionVietnam@dev.azure.com/NorthstarPrecisionVietnam/PolarisNNet/_git/local_orch
    ```

    You should now have both repos on your local machine. 

1. ##Creating a New Branch

    Create a new branch for each Jetson station:

    ```
    git checkout -b <insert branch name>
    ```

    Branch name should be the IP address.  Or at least that is what the others are named after. 

    Now save the changes to Azure Devops:

    ```
    git push --set-upstream origin <branch name>
    ```

    Replace <branch name> with the actual branch name



# Navigating Azure Devops
---
TODO: Describe the different functions of Azure Devops. 


# Git Commands
--- 
Listed below are common git commands needed for updating files as you edit:

| Git Command | Action |   
|-----------|:-----------| 
| git clone | Copies repository onto your local machine | 
| git add | Adds files to be commited | 
| git commit -m "MESSAGE"| Saves snapshots of files added to local machine only. Replace MESSAGE with edit message |
| git status | States some difference between the local branch and the master file |
| git push | Saves all committed files to the server.  In this case that is Azure Devops |
| git pull | Downloads the latest versions of all the files onto your local machine |
| git log | Displays a log of all the changes in the repository |
| git branch | States all the branches and which branch you currently reside in |
| git checkout -b <name> | Creates a new branch.  Replace <name> with the new branch name|
| git merge <branch name> | Merges the branch back to the master file on the server |

# Contribute
---
TODO: Explain how other users and developers can contribute to make your code better. 

If you want to learn more about creating good readme files then refer the following [guidelines](https://docs.microsoft.com/en-us/azure/devops/repos/git/create-a-readme?view=azure-devops). You can also seek inspiration from the below readme files:
- [ASP.NET Core](https://github.com/aspnet/Home)
- [Visual Studio Code](https://github.com/Microsoft/vscode)
- [Chakra Core](https://github.com/Microsoft/ChakraCore)