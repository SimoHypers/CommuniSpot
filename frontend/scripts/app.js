
document.addEventListener("DOMContentLoaded", () => {
    //Here I will check if the page is the callback page
    const currentUrl = window.location.href;
    if(currentUrl.includes("/callback")){
        handleCallback();
    }
})

async function handleCallback(){
    //Extracting the auth code from the URL
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get("code");

    if(!code){
        console.error("Authorization code not found");
        return;
    }

    try{
        //Here I will fetch the tokens from the main.py
        const response = await fetch(`https://localhost:8000/callback?code=${code}`);
        if(!response.ok){
            throw new Error(`Error fetching tokens: ${response.status}`);
        }

        const tokenData = await response.json();
        const accessToken = tokenData.access_token;
        const refreshToken = tokenData.refreshToken;

        localStorage.setItem("access_token", accessToken);
        localStorage.setItem("refresh_token", refreshToken);
        
        console.log("Access Token: ", accessToken);
        console.log("Refresh Token: ", refreshToken);

        window.location.href = "/static/home.html";     //This will redirect users to the homepage

    }

    catch(error){
        console.error("Failed to handle callback:", error);
    }
}
