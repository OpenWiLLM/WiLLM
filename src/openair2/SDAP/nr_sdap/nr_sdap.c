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

#define _GNU_SOURCE

#include "nr_sdap.h"
#include <pthread.h>

static void reblock_tun_socket(int sock)
{
  int f;

  f = fcntl(sock, F_GETFL, 0);
  f &= ~(O_NONBLOCK);
  if (fcntl(sock, F_SETFL, f) == -1) {
    LOG_E(SDAP, "reblock_tun_socket failed\n");
    exit(1);
  }
}

static void *ue_tun_read_thread(void *arg)
{
  nr_sdap_entity_t *entity = (nr_sdap_entity_t *)arg;
  char rx_buf[NL_MAX_PAYLOAD];
  int len;
  protocol_ctxt_t ctxt;

  int rb_id = 1;
  char thread_name[64];
  sprintf(thread_name, "ue_tun_read%d\n", entity->pdusession_id);
  pthread_setname_np( pthread_self(), thread_name);
  while (1) {
    len = read(entity->pdusession_sock, &rx_buf, NL_MAX_PAYLOAD);

    if (entity->stop_thread) break;

    if (len == -1) {
      LOG_E(PDCP, "%s:%d:%s: fatal\n", __FILE__, __LINE__, __FUNCTION__);
      exit(1);
    }

    LOG_D(PDCP, "%s(): pdusession_sock read returns len %d\n", __func__, len);

    ctxt.module_id = 0;
    ctxt.enb_flag = 0;
    ctxt.instance = 0;
    ctxt.frame = 0;
    ctxt.subframe = 0;
    ctxt.eNB_index = 0;
    ctxt.brOption = 0;
    ctxt.rntiMaybeUEid = entity->ue_id;

    bool dc = SDAP_HDR_UL_DATA_PDU;

    entity->tx_entity(entity, &ctxt, SRB_FLAG_NO, rb_id, RLC_MUI_UNDEFINED, RLC_SDU_CONFIRM_NO, len, (unsigned char *)rx_buf, PDCP_TRANSMISSION_MODE_DATA, NULL, NULL, entity->qfi, dc);
  }

  return NULL;
}

void start_sdap_tun_ue(nr_sdap_entity_t *entity)
{
  reblock_tun_socket(entity->pdusession_sock);

  if (pthread_create(&entity->pdusession_thread, NULL, ue_tun_read_thread, (void*)entity) != 0) {
    LOG_E(PDCP, "%s:%d:%s: fatal\n", __FILE__, __LINE__, __FUNCTION__);
    exit(1);
  }
}

bool sdap_data_req(protocol_ctxt_t *ctxt_p,
                   const ue_id_t ue_id,
                   const srb_flag_t srb_flag,
                   const rb_id_t rb_id,
                   const mui_t mui,
                   const confirm_t confirm,
                   const sdu_size_t sdu_buffer_size,
                   unsigned char *const sdu_buffer,
                   const pdcp_transmission_mode_t pt_mode,
                   const uint32_t *sourceL2Id,
                   const uint32_t *destinationL2Id,
                   const uint8_t qfi,
                   const bool rqi,
                   const int pdusession_id) {
  nr_sdap_entity_t *sdap_entity;
  sdap_entity = nr_sdap_get_entity(ue_id, pdusession_id);

  if(sdap_entity == NULL) {
    LOG_E(SDAP, "%s:%d:%s: Entity not found with ue: 0x%"PRIx64" and pdusession id: %d\n", __FILE__, __LINE__, __FUNCTION__, ue_id, pdusession_id);
    return 0;
  }

  bool ret = sdap_entity->tx_entity(sdap_entity,
                                    ctxt_p,
                                    srb_flag,
                                    rb_id,
                                    mui,
                                    confirm,
                                    sdu_buffer_size,
                                    sdu_buffer,
                                    pt_mode,
                                    sourceL2Id,
                                    destinationL2Id,
                                    qfi,
                                    rqi);
  return ret;
}

void sdap_data_ind(rb_id_t pdcp_entity,
                   int is_gnb,
                   bool has_sdap_rx,
                   int pdusession_id,
                   ue_id_t ue_id,
                   char *buf,
                   int size) {
  nr_sdap_entity_t *sdap_entity;
  sdap_entity = nr_sdap_get_entity(ue_id, pdusession_id);

  if (sdap_entity == NULL) {
    LOG_E(SDAP, "%s:%d:%s: Entity not found for ue rnti/ue_id: %lx and pdusession id: %d\n", __FILE__, __LINE__, __FUNCTION__, ue_id, pdusession_id);
    return;
  }

  sdap_entity->rx_entity(sdap_entity,
                         pdcp_entity,
                         is_gnb,
                         has_sdap_rx,
                         pdusession_id,
                         ue_id,
                         buf,
                         size);
}
