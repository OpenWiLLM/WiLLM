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

#ifndef _UE_SLICE_MANAGER_H_
#define _UE_SLICE_MANAGER_H_

typedef struct __attribute__((__packed__)) {
  int sst;
  int hplmn_sst;
  int sd;
  int hplmn_sd;
} nr_nas_msg_snssai_t;

typedef struct __attribute__((__packed__)) {
  uint8_t sdap_entity_number;
  uint8_t pdusession_id;
  nr_nas_msg_snssai_t s_nssai;
} sdap_entity_info_el_t;

typedef struct __attribute__((__packed__)) {
  uint16_t num_elements;
  sdap_entity_info_el_t element[8];
} sdap_entity_info_t;

#endif
