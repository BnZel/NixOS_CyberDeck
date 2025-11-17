#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <sys/socket.h>
#include <netdb.h>
#include <pthread.h>

#include "../include/network.h"

struct glove glove_ = {0};
struct servo servo_ = {0};
pthread_mutex_t glove_data;

void parseData(struct glove *glove_, struct servo *servo_, char buffer[])
{
    pthread_mutex_lock(&glove_data);

    sscanf(buffer, "%[^,],%lu,%lu,%lu,%lu,%lu,%f,%f,%f",
        glove_->name, &glove_->A2, &glove_->A3, &glove_->A4, 
        &glove_->D32, &glove_->D33, &glove_->x, &glove_->y, &glove_->z);
    
    servo_->s1 = glove_->A3;
    servo_->s2 = glove_->A4;
    servo_->s3 = glove_->D32;
    servo_->s4 = glove_->D33; 
        
    pthread_mutex_unlock(&glove_data);

    // printf("%s || A2: %lu | A3: %lu | A4: %lu | D32: %lu | D33: %lu | x: %f | y: %f | z: %f\n",\
    //     glove_->name,glove_->A2,glove_->A3,glove_->A4,glove_->D32,glove_->D33,glove_->x,glove_->y,glove_->z);  
}

void sendData(int clientSocket, struct glove *glove, struct servo *servo)
{
    char TxBuffer[BUFFER_SIZE] = {0};
    pthread_mutex_lock(&glove_data);

    sprintf(TxBuffer,"%lu,%lu,%lu,%lu",servo->s1,servo->s2,servo->s3,servo->s4);

    pthread_mutex_unlock(&glove_data);

    send(clientSocket, TxBuffer, strlen(TxBuffer), 0);

    printf("SERVERDECK || S1: %lu | S2: %lu | S3: %lu | S4: %lu \n",\
         servo->s1, servo->s2, servo->s3, servo->s4);
}

void *manageClient(void *args)
{
    int clientSocket = *(int *) args;
    char RxBuffer[BUFFER_SIZE] = {0};
    char TxBuffer[] = "Server Response: Connected!";

    send(clientSocket, TxBuffer, sizeof(TxBuffer), 0);

    while(true)
    {        
        int received = recv(clientSocket, RxBuffer, sizeof(RxBuffer), 0);
        if(received == 0){printf("\n\nClient disconnected...\n"); break;}
        
        if(received > 0)
        {
            RxBuffer[received] = '\0';
            if(strstr(RxBuffer,"GLOVE"))
            {
                parseData(&glove_, &servo_, RxBuffer);
            } 

            if(strstr(RxBuffer,"SERVERDECK"))
            {   
                sendData(clientSocket, &glove_, &servo_);
            }
        }
    }

    printf("Client socket closed...\n\n");
    close(clientSocket);
}

void startServer()
{
    int serverSocket;
    serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if(serverSocket == 0){printf("Error creating server socket...\n"); exit(1);}
    printf("Server socket created\n");

    if (setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, &(int){1}, sizeof(int)) < 0){error("setsockopt(SO_REUSEADDR) failed");}

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

    pthread_mutex_init(&glove_data, NULL);

    while(true)
    {
        clientSocket = accept(serverSocket, (struct sockaddr *) &svrAddress, (socklen_t *) &lenAddress);

        if(clientSocket < 0){
            printf("Error accepting new connections...\n"); 
            exit(1);
        }

        printf("Listening to incoming connections\n\n");

        // multi-threading
        pthread_t tid;
        if(pthread_create(&tid, NULL, manageClient, (void *)&clientSocket) != 0){
            printf("Error creating thread...\n");
	    free(clientSocket); 
            exit(1);
        }
        else {
            pthread_detach(tid); 
        }
    }

	close(serverSocket);
}
