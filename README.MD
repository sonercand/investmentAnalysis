
## Installation
1) create a python  env


          python -m venv venv
     
 
if not workings try this first
     
     
          pip install virtualenv

and repeat step 1

2) activate the environment

    
          venv\Scripts\activate


3) install requirements
    
    
          pip install -r requirements.txt


4) Check everythings is working:

<<<<<<< HEAD
    python -m app.py
    
    
=======
          
          python -m app.py
          

## Generic git commands:
1) add remote path to enable push and pull (Do this once)

          
          git remote add origin git@github.com:sonercand/PortAI.git
     
     
2)After doing some work  save your changes:
     
         
          git add . 
          git commit -m"Commit message"

3) Push your changes to the remote main branch
     
          
          git push origin main

if it fails try pulling first
4) Pull changes from remote

          
          git pull origin main
>>>>>>> 3b7f85e7bccfd4712692d0281c78bb3749e16af7
