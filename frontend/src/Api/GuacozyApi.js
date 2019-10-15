import axios from "axios";

export default class GuacadminApi {
    apiInstance = axios.create({
        baseURL: '/api/',
        timeout: 1000,
        xsrfCookieName: "csrftoken",
        xsrfHeaderName: "X-CSRFToken",
    });

    constructor() {
        this.apiInstance.interceptors.response.use(response => {
                return response;
            }, (error) => {
                if (error.response) {
                    // The request was made and the server responded with a status code
                    // that falls out of the range of 2xx
                    console.log("Api error:");
                    console.log("Data: ");
                    console.log(error.response.data);
                    console.log("Status: " + error.response.status);
                    console.log("Headers: ");
                    console.log(error.response.headers);

                } else if (error.request) {
                    // The request was made but no response was received
                    // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
                    // http.ClientRequest in node.js
                    console.log("Request: " + error.request);
                } else {
                    // Something happened in setting up the request that triggered an Error
                    console.log('Error: ', error.message);
                }

                return Promise.reject(error);
            }
        );

    }

    getCurrentUser() {
        return this.apiInstance.get("/users/current/");
    }

    logout() {
        return  this.apiInstance.get("/accounts/logout/",{baseURL:"/"})
    }

    getConnections() {
        return this.apiInstance.get("/connections/tree");
    }
    
    getTickets() {
        return this.apiInstance.get("/tickets/");
    }
    
    deleteTicket(id, callback) {
        return this.apiInstance.delete("/tickets/" + id + "")
            .then(() => {
                callback && callback();
            })

    }
    
     updateNodeLocation = ({id, parentid, isFolder}) => {
        let bodyFormData = new FormData();
        bodyFormData.set('parent', parentid);
        
        if (isFolder) {
            return this.apiInstance.patch("/folders/" + id + "/", bodyFormData);
        }else{
            return this.apiInstance.patch("/connections/" + id + "/", bodyFormData);
        }
    }
}