Named Credentials allows to have user owned credentials for a connection, which can be referenced by common name. 

Example:  
You have several employees who support customer's Contoso Corp. infrastructure.   
Each of your employees has a user in Contoso Corp. Active Directory.

You create a **Named Credentials** object "@contoso.corp" and each of your employees can create a **Personal Named Credential** referencing this **Named Credentials** object.

This allows connections without requiring password but with different password for every user. 

If a user doesn't have a **Personal Named Credential** required for this connection he will be asked for login in those cases:
- SSH connection
- RDP connection with RDP security

User will not be able to connect if RDP connection uses NLA or TLS security, 
because this connection requires username/password to start network connection and 
will not show login screen for unautheticated users.

        