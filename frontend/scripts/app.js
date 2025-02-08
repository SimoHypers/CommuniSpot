
document.addEventListener("DOMContentLoaded", () => {
    //Here I will check if the page is the callback page
    if(window.location.pathname.includes("callback.html")){
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
        
        const response = await fetch(`http://localhost:8000/callback?code=${code}`);
        if(!response.ok){
            throw new Error(`Error fetching tokens: ${response.status}`);
        }

        const tokenData = await response.json();
        const accessToken = tokenData.accessToken;
        const refreshToken = tokenData.refreshToken;

        localStorage.setItem("access_token", tokenData.accessToken);
        localStorage.setItem("refresh_token", tokenData.refreshToken);

        console.log("Access Token: ", accessToken);
        console.log("Refresh Token: ", refreshToken);

        window.location.href = "http://localhost:8000/static/home.html";

    }

    catch(error){
        console.error("Failed to handle callback:", error);
    }
}
