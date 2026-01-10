    const form = document.getElementById("dataForm");
    
    form.addEventListener("submit", async function(event){
        event.preventDefault();

    
        const playerTag = document.getElementById("playerTag").value;
        const apiToken = document.getElementById("apiToken").value;


        const dataToSend = { 
            playerTag: playerTag, 
            apiToken: apiToken 
        };

        const response = await fetch('http://127.0.0.1:5000/verify-user', {
            
            method: 'POST', 
            
            headers: { 
                'Content-Type': 'application/json' 
            },
            
            body: JSON.stringify(dataToSend) 
        });


        const result = await response.json();
        
        if(result.message == true){ //change back to true
            window.location.href ="/dashboard";
        }
        
        else{

            document.getElementById("result").innerText =
      "Result: " + result.receivedPlayerTag + "\n able to recruit: " + result.recruit_status ;
                
        }
    })
