import axios from "axios";
import {DEFAULT_VALIDITY_PERIOD} from "../settings";

export default class GuacadminApi {
    apiInstance = axios.create({
        baseURL: '/api/',
        timeout: 30000,
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

    getUsers() {
        return this.apiInstance.get("/users/");
    }

    getCurrentUser() {
        return this.apiInstance.get("/users/current/");
    }

    logout() {
        return this.apiInstance.get("/accounts/logout/", {baseURL: "/"})
    }

    getConnections() {
        return this.apiInstance.get("/connections/tree");
    }

    getTickets() {
        return this.apiInstance.get("/tickets/");
    }

    createTicket(connectionid, userid, callback) {
        let data = {
            connection: connectionid,
            validityperiod: DEFAULT_VALIDITY_PERIOD,
            user: userid,
        };

        return this.apiInstance.post("/tickets/", data)
            .then(response => {
                callback(response.data.id);
            })
    }

    duplicateTicket(originalTicketid, callback) {
        return this.apiInstance.post("/tickets/duplicate/" + originalTicketid + "/")
            .then(response => {
                let ticketuuid = response.data.id;
                callback(ticketuuid);
            })
    }

    deleteTicket(id, callback) {
        return this.apiInstance.delete("/tickets/" + id + "")
            .then(() => {
                callback && callback();
            })

    }

    shareTicket({ticketid, userid, validityPeriod, control}) {
        let bodyFormData = new FormData();
        bodyFormData.set('userid', userid);
        bodyFormData.set('validityperiod', validityPeriod);
        bodyFormData.set('control', control);
        return this.apiInstance.post("/tickets/share/" + ticketid + "/", bodyFormData);
    }

    updateNodeLocation = ({id, parentid, newName, isFolder}) => {
        let bodyFormData = new FormData();

        if (parentid) {
            bodyFormData.set('parent', parentid);
        }

        if (newName) {
            bodyFormData.set('name', newName);
        }

        if (isFolder) {
            return this.apiInstance.patch("/folders/" + id + "/", bodyFormData);
        } else {
            return this.apiInstance.patch("/connections/" + id + "/", bodyFormData);
        }
    };

    createFolder = ({parendId, name}) => {
        let bodyFormData = new FormData();
        bodyFormData.set('parent', parendId);
        bodyFormData.set('name', name);
        return this.apiInstance.post("/folders/", bodyFormData);
    };

    deleteFolder = ({id}) => {
        return this.apiInstance.delete("/folders/" + id + "/");
    };

    // renameNode = ({id, newName, isFolder}) => {
    //     let bodyFormData = new FormData();
    //     bodyFormData.set('name', newName);
    //    
    //     if (isFolder) {
    //         return this.apiInstance.patch("/folders/" + id + "/", bodyFormData);
    //     } else {
    //         return this.apiInstance.patch("/connections/" + id + "/", bodyFormData);
    //     }        
    // };
}