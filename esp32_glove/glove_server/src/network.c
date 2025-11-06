#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <sys/socket.h>
#include <netdb.h>
#include <pthread.h>

#include "../include/network.h"

void parseData(struct glove glove_, char buffer[])
{
    char *token;

    token = strtok(buffer,",");
    glove_.A2 = atoll(token);
    
    token = strtok(NULL,",");
    glove_.A3 = atoll(token);

    token = strtok(NULL,",");
    glove_.A4 = atoll(token);

    token = strtok(NULL,",");
    glove_.D32 = atoll(token);   
    
    token = strtok(NULL,",");
    glove_.D33 = atoll(token);

    token = strtok(NULL,",");
    glove_.x = atof(token);

    token = strtok(NULL,",");
    glove_.y = atof(token);

    token = strtok(NULL,",");
    glove_.z = atof(token);

    printf("A2: %lu | A3: %lu | A4: %lu | D32: %lu | D33: %lu | x: %f | y: %f | z: %f\n",\
        glove_.A2,glove_.A3,glove_.A4,glove_.D32,glove_.D33,glove_.x,glove_.y,glove_.z);    
}

void *manageClient(void *args)
{
    int clientSocket = *(int *) args;
    char RxBuffer[BUFFER_SIZE] = {0};
    char TxBuffer[] = "Server Response: Connected!";

    send(clientSocket, TxBuffer, sizeof(TxBuffer), 0);

    struct glove glove_;

    while(true)
    {        
        int received = recv(clientSocket, RxBuffer, sizeof(RxBuffer), 0);
        if(received == 0){printf("Client disconnected...\n"); break;}
        
        if(received > 0)
        {
            RxBuffer[received] = '\0';
            parseData(glove_, RxBuffer);
        }
    }

    printf("Client socket closed...");
    close(clientSocket);
}

void startServer()
{
    int serverSocket;
    serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if(serverSocket == 0){printf("Error creating server socket...\n"); exit(1);}
    printf("Server socket created\n");

    struct sockaddr_in svrAddress;
    svrAddress.sin_family = AF_INET;
    svrAddress.sin_addr.s_addr = htonl(INADDR_ANY);
    svrAddress.sin_port = htons(PORT);

    int lenAddress = sizeof(svrAddress);

    int bindResult = bind(serverSocket, (struct sockaddr * ) &svrAddress, lenAddress);
    if(bindResult < 0){printf("Error binding to socket...\n"); exit(1);}

    int listenResult = listen(serverSocket, NUM_CLIENTS);
    if(listenResult < 0){printf("Error listening to socket...\n"); exit(1);}
    printf("Listening to socket\n");

    int clientSocket;

    while(true)
    {
        clientSocket = accept(serverSocket, (struct sockaddr *) &svrAddress, (socklen_t *) &lenAddress);

        if(clientSocket < 0){
            printf("Error accepting new connections...\n"); 
            exit(1);
        }
        printf("Listening to incoming connections");

        // multi-threading
        pthread_t tid;
        if(pthread_create(&tid, NULL, manageClient, (void *)&clientSocket) != 0){
            printf("Error creating thread...\n"); 
            exit(1);
        }
        else {
            pthread_detach(tid); 
        }
    }

	close(serverSocket);
}
