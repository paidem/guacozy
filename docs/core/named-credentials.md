_**Named Credentials**_ allows to store per user credentials, which can be referenced by common name. 

User's personal instance of _**Named Credentials**_ is called _**Personal Named Credentials**_

_**Personal Named Credentials**_ name always starts with **@** symbol

#### Example  
You have several employees who support customer's Contoso Corp. infrastructure.   
Each of your employees has a user in Contoso Corp. Active Directory.

You create a _**Named Credentials**_ object `@contoso.corp` and each of your employees can create a _**Personal Named Credential**_ referencing this _**Named Credentials**_ object.

This allows connections without requiring password but with different password for every user. 

If a user doesn't have a _**Personal Named Credential**_ required for this connection he will be asked for login in those cases:
- SSH connection
- RDP connection with RDP security

User will not be able to connect if RDP connection uses NLA or TLS security, 
because this connection requires username/password to start network connection and 
will not show login screen for unauthenticated users.

        