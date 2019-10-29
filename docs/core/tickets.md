Ticket is a method to allow time limited access to a connection.

Ticket references a connection and has a time limit, defined by **a)** time when ticket was created and **b)** it's validity period.

Tickets with expired validity are deleted automatically. 

Each ticket has an **Author** (who _created_ a ticket) and **User** (who can _use_ a ticket).  
If a user has opened a connection, author and user are the same.  

User can **share** a ticket with another user. In this case tickets share **guacd session** which means they see the same view and if control is allowed - use session simultaneously 