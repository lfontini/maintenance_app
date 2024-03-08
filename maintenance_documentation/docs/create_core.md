# Tutorial: Creating a Core

## Accessing Core Creation Option
To create a core, start by selecting the "Create Core" option from the sidebar.

![Sidebar create core option](/media/navbar.png)

## Completing the Form
Once you've chosen to create a core, a form will appear for you to fill out.

![Core Form](/media/form.png)

## Activity Related to Core
![Core Activity](/media/activity_releted.png)

## Affected Services
When selecting routers and switches that will be affected, the application retrieves all relevant data from the Gogs repository.

![Services Affected](/media/services_affected.png)


## Add Services
If needed you are able to add new service that supposted be affected, if you drop it an NNI service, all attached services comes together


![Services add](/media/addservices.png)

## NNIs (Network-to-Network Interfaces)
During the process, if the application receives an NNI, it automatically checks all services attached to this interface and updates the services affected table accordingly.

## Deleting Services
For cancelled services, by default, you don't need to open a ticket. Deleting them is optional or may be necessary for other services that need to be removed from the form.

![Deleting Services](/media/services_affected02.png)

## Error Handling
In case of errors, the application provides appropriate feedback to guide the user.

![Error Handling](/media/error.png)

## Generating Tickets
Once the core creation process is complete, the application generates tickets for further action if necessary.

![Generating Tickets](/media/generateticket.png)

When the devices arrive at the customer site, the engineer only needs to connect to the interface, and the service will be configured automatically
