/*
 * Licensed to the OpenAirInterface (OAI) Software Alliance under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The OpenAirInterface Software Alliance licenses this file to You under
 * the OAI Public License, Version 1.1  (the "License"); you may not use this file
 * except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.openairinterface.org/?page_id=698
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *-------------------------------------------------------------------------------
 * For more information about the OpenAirInterface (OAI) Software Alliance:
 *      contact@openairinterface.org
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdbool.h>

#include "ue_slice_manager.h"

#define SERVER_ADDRESS "127.0.0.1"
#define SERVER_PORT 34000

static void display_sdap_info(sdap_entity_info_t info)
{
  printf("Number of SDAP entities: %d\n", info.num_elements);
  for (int i = 0; i < info.num_elements; i++) {
    printf("--SDAP entity number: %d\n", info.element[i].sdap_entity_number);
    printf("--PDU session id    : %d\n", info.element[i].pdusession_id);
    printf("\n");
  }
}

static void display_allowed_nssai(nr_nas_msg_snssai_t nssai[8])
{
  printf("List of allowed NSSAI from core network\n");
  for (int i = 0; i < 8; i++) {
    printf("S-NSSAI index: %d\n", i);
    printf("--SST: %d\n", nssai[i].sst);
    printf("--SD : %d\n", nssai[i].sd);
    printf("\n");
  }
}

static bool check_pdu_exists(int id, sdap_entity_info_t info)
{
  bool ret = false;
  for (int i = 0; i < info.num_elements; i++) {
    if (id == info.element[i].pdusession_id) {
      ret = true;
      break;
    }
  }
  return ret;
}

static void get_user_command(uint8_t cmd_input[8], sdap_entity_info_t info)
{
  printf("Enter any of the following commands to send\n");
  printf("--Request new PDU session: 1\n");
  printf("--Request deletion of PDU session: 2\n");
  printf("--Request active PDU session info: 3\n");
  printf("\n");

  int cmd;
  int pdu_id;
  int snssai_idx;
  bool pdu_id_exists = false;
  printf("Enter the option here: ");
  scanf("%d", &cmd);

  if (cmd == 1) {
    printf("Enter new PDU session id: ");
    scanf("%d", &pdu_id);
    pdu_id_exists = check_pdu_exists(pdu_id, info);
    if (pdu_id_exists) {
      printf("Entered PDU is already active\n");
      get_user_command(cmd_input, info);
    } else {
      cmd_input[0] = cmd;
      cmd_input[1] = pdu_id;
    }
    printf("Enter S-NSSAI index from allowed NSSAI list: ");
    scanf("%d", &snssai_idx);
    if (snssai_idx < 7 && snssai_idx >= 0) {
      cmd_input[2] = snssai_idx;
    } else {
      printf("Entered S-NSSAI index out of bound. Should be from 0 to 7.\n");
      get_user_command(cmd_input, info);
    }
  } else if (cmd == 2) {
    printf("Enter PDU session id to delete: ");
    scanf("%d", &pdu_id);
    pdu_id_exists = check_pdu_exists(pdu_id, info);
    if (pdu_id_exists) {
      cmd_input[0] = cmd;
      cmd_input[1] = pdu_id;
    } else {
      printf("Entered PDU session not active\n");
      get_user_command(cmd_input, info);
    } 
  } else if (cmd == 3) {
    cmd_input[0] = cmd;
  } else {
    printf("Invalid option\n");
    get_user_command(cmd_input, info);
  }
}

int main() {
  int sock = 0;
  int valread;
  struct sockaddr_in serv_addr;
  char buffer[1024] = {0};
  uint8_t send_buf[8] = {0};

  // create socket
  if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
    printf("\n Socket creation error \n");
    return -1;
  }

  // fill in server address and port
  serv_addr.sin_family = AF_INET;
  serv_addr.sin_port = htons(SERVER_PORT);

  // Convert IPv4 and IPv6 addresses from text to binary form
  if(inet_pton(AF_INET, SERVER_ADDRESS, &serv_addr.sin_addr)<=0) {
    printf("\nInvalid address/ Address not supported \n");
    return -1;
  }

  // connect to server
  printf("Connecting to %s:%d\n", SERVER_ADDRESS, SERVER_PORT);
  if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
    printf("Connection Failed\n");
    return -1;
  }

  while (true) {
    // send message to server
    if (send(sock, send_buf, sizeof(send_buf), 0) < 0) {
      printf("Error sending to server\n");
      break;
    }
    printf("Command sent to server\n");

    // receive message from server
    valread = read(sock, buffer, 1024);
    if (valread < 0) {
      printf("Received number of bytes is less than 0\n");
      break;
    }
    printf("Message received from server: %d\n", valread);
    nr_nas_msg_snssai_t nssai[8];
    memcpy(nssai, buffer, sizeof(nssai));
    display_allowed_nssai(nssai);

    sdap_entity_info_t sdap_info;
    memcpy(&sdap_info, buffer+sizeof(nssai), sizeof(sdap_info));
    display_sdap_info(sdap_info);
    // get user command
    get_user_command(send_buf, sdap_info);
  }
  // close socket
  close(sock);
  return 0;
}

