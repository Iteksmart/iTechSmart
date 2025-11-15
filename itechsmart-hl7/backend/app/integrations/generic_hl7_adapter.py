"""
Generic HL7 v2.x Adapter
Works with any EMR system that supports HL7 v2.x messaging
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import socket

logger = logging.getLogger(__name__)


class GenericHL7Adapter:
    """
    Generic HL7 v2.x Adapter
    Supports bidirectional HL7 messaging with any compliant EMR system
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.host = config.get('host')
        self.port = config.get('port', 2575)
        self.sending_application = config.get('sending_application', 'iTechSmart')
        self.sending_facility = config.get('sending_facility', 'iTechSmart')
        self.receiving_application = config.get('receiving_application')
        self.receiving_facility = config.get('receiving_facility')
        self.use_mllp = config.get('use_mllp', True)
        self.message_handlers: Dict[str, Callable] = {}
        self.listener_task = None
        
    async def send_message(self, hl7_message: str) -> Optional[str]:
        """
        Send HL7 message and wait for ACK
        """
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            
            # Wrap with MLLP framing if enabled
            if self.use_mllp:
                message = f"\x0b{hl7_message}\x1c\x0d".encode('utf-8')
            else:
                message = hl7_message.encode('utf-8')
            
            writer.write(message)
            await writer.drain()
            
            # Wait for ACK
            response = await asyncio.wait_for(reader.read(4096), timeout=30.0)
            
            writer.close()
            await writer.wait_closed()
            
            # Parse response
            if self.use_mllp:
                ack_message = response.decode('utf-8').strip('\x0b\x1c\x0d')
            else:
                ack_message = response.decode('utf-8')
            
            logger.info(f"HL7 message sent successfully, ACK received")
            return ack_message
            
        except asyncio.TimeoutError:
            logger.error("Timeout waiting for ACK")
            return None
        except Exception as e:
            logger.error(f"Failed to send HL7 message: {e}")
            return None
    
    async def send_adt_a01(self, patient_data: Dict) -> Optional[str]:
        """
        Send ADT^A01 (Patient Admit) message
        """
        message = self._build_adt_message('A01', patient_data)
        return await self.send_message(message)
    
    async def send_adt_a02(self, patient_data: Dict) -> Optional[str]:
        """
        Send ADT^A02 (Patient Transfer) message
        """
        message = self._build_adt_message('A02', patient_data)
        return await self.send_message(message)
    
    async def send_adt_a03(self, patient_data: Dict) -> Optional[str]:
        """
        Send ADT^A03 (Patient Discharge) message
        """
        message = self._build_adt_message('A03', patient_data)
        return await self.send_message(message)
    
    async def send_adt_a04(self, patient_data: Dict) -> Optional[str]:
        """
        Send ADT^A04 (Patient Registration) message
        """
        message = self._build_adt_message('A04', patient_data)
        return await self.send_message(message)
    
    async def send_adt_a08(self, patient_data: Dict) -> Optional[str]:
        """
        Send ADT^A08 (Patient Update) message
        """
        message = self._build_adt_message('A08', patient_data)
        return await self.send_message(message)
    
    async def send_oru_r01(self, lab_data: Dict) -> Optional[str]:
        """
        Send ORU^R01 (Observation Result) message
        """
        message = self._build_oru_message(lab_data)
        return await self.send_message(message)
    
    async def send_orm_o01(self, order_data: Dict) -> Optional[str]:
        """
        Send ORM^O01 (Order Message) message
        """
        message = self._build_orm_message(order_data)
        return await self.send_message(message)
    
    async def send_mdm_t02(self, document_data: Dict) -> Optional[str]:
        """
        Send MDM^T02 (Document Notification) message
        """
        message = self._build_mdm_message(document_data)
        return await self.send_message(message)
    
    def _build_adt_message(self, event_type: str, patient_data: Dict) -> str:
        """
        Build ADT message
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        message_control_id = f"{timestamp}{patient_data.get('mrn', '')}"
        
        segments = []
        
        # MSH - Message Header
        msh = (
            f"MSH|^~\\&|{self.sending_application}|{self.sending_facility}|"
            f"{self.receiving_application}|{self.receiving_facility}|"
            f"{timestamp}||ADT^{event_type}|{message_control_id}|P|2.5"
        )
        segments.append(msh)
        
        # EVN - Event Type
        evn = f"EVN|{event_type}|{timestamp}"
        segments.append(evn)
        
        # PID - Patient Identification
        pid = self._build_pid_segment(patient_data)
        segments.append(pid)
        
        # PV1 - Patient Visit
        if 'visit' in patient_data:
            pv1 = self._build_pv1_segment(patient_data['visit'])
            segments.append(pv1)
        
        return '\r'.join(segments)
    
    def _build_pid_segment(self, patient_data: Dict) -> str:
        """
        Build PID segment
        """
        mrn = patient_data.get('mrn', '')
        last_name = patient_data.get('last_name', '')
        first_name = patient_data.get('first_name', '')
        middle_name = patient_data.get('middle_name', '')
        dob = patient_data.get('birth_date', '')
        gender = patient_data.get('gender', '')
        ssn = patient_data.get('ssn', '')
        
        address = patient_data.get('address', {})
        street = address.get('street', '')
        city = address.get('city', '')
        state = address.get('state', '')
        zip_code = address.get('zip', '')
        
        phone = patient_data.get('phone', '')
        
        pid = (
            f"PID|1||{mrn}^^^MRN||{last_name}^{first_name}^{middle_name}||"
            f"{dob}|{gender}|||{street}^^{city}^{state}^{zip_code}||"
            f"{phone}|||||||{ssn}"
        )
        
        return pid
    
    def _build_pv1_segment(self, visit_data: Dict) -> str:
        """
        Build PV1 segment
        """
        patient_class = visit_data.get('patient_class', 'O')
        location = visit_data.get('location', '')
        attending_doctor = visit_data.get('attending_doctor', '')
        admit_date = visit_data.get('admit_date', '')
        
        pv1 = (
            f"PV1|1|{patient_class}|{location}|||{attending_doctor}|||||||||||"
            f"|||||||||||||||||||||||{admit_date}"
        )
        
        return pv1
    
    def _build_oru_message(self, lab_data: Dict) -> str:
        """
        Build ORU^R01 (Lab Results) message
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        message_control_id = f"{timestamp}{lab_data.get('patient_mrn', '')}"
        
        segments = []
        
        # MSH
        msh = (
            f"MSH|^~\\&|{self.sending_application}|{self.sending_facility}|"
            f"{self.receiving_application}|{self.receiving_facility}|"
            f"{timestamp}||ORU^R01|{message_control_id}|P|2.5"
        )
        segments.append(msh)
        
        # PID
        pid = self._build_pid_segment(lab_data.get('patient', {}))
        segments.append(pid)
        
        # OBR - Observation Request
        obr = self._build_obr_segment(lab_data)
        segments.append(obr)
        
        # OBX - Observation Results
        for i, result in enumerate(lab_data.get('results', []), start=1):
            obx = self._build_obx_segment(i, result)
            segments.append(obx)
        
        return '\r'.join(segments)
    
    def _build_obr_segment(self, lab_data: Dict) -> str:
        """
        Build OBR segment
        """
        order_id = lab_data.get('order_id', '')
        test_code = lab_data.get('test_code', '')
        test_name = lab_data.get('test_name', '')
        observation_date = lab_data.get('observation_date', datetime.now().strftime('%Y%m%d%H%M%S'))
        
        obr = (
            f"OBR|1|{order_id}||{test_code}^{test_name}|||"
            f"{observation_date}|||||||||||||||||||F"
        )
        
        return obr
    
    def _build_obx_segment(self, sequence: int, result: Dict) -> str:
        """
        Build OBX segment
        """
        test_code = result.get('test_code', '')
        test_name = result.get('test_name', '')
        value = result.get('value', '')
        unit = result.get('unit', '')
        reference_range = result.get('reference_range', '')
        abnormal_flag = result.get('abnormal_flag', '')
        status = result.get('status', 'F')
        
        obx = (
            f"OBX|{sequence}|NM|{test_code}^{test_name}||{value}|{unit}|"
            f"{reference_range}|{abnormal_flag}|||{status}"
        )
        
        return obx
    
    def _build_orm_message(self, order_data: Dict) -> str:
        """
        Build ORM^O01 (Order) message
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        message_control_id = f"{timestamp}{order_data.get('patient_mrn', '')}"
        
        segments = []
        
        # MSH
        msh = (
            f"MSH|^~\\&|{self.sending_application}|{self.sending_facility}|"
            f"{self.receiving_application}|{self.receiving_facility}|"
            f"{timestamp}||ORM^O01|{message_control_id}|P|2.5"
        )
        segments.append(msh)
        
        # PID
        pid = self._build_pid_segment(order_data.get('patient', {}))
        segments.append(pid)
        
        # ORC - Common Order
        orc = self._build_orc_segment(order_data)
        segments.append(orc)
        
        # OBR - Observation Request
        obr = self._build_obr_segment(order_data)
        segments.append(obr)
        
        return '\r'.join(segments)
    
    def _build_orc_segment(self, order_data: Dict) -> str:
        """
        Build ORC segment
        """
        order_control = order_data.get('order_control', 'NW')
        order_id = order_data.get('order_id', '')
        ordering_provider = order_data.get('ordering_provider', '')
        
        orc = (
            f"ORC|{order_control}|{order_id}||||||||"
            f"{ordering_provider}"
        )
        
        return orc
    
    def _build_mdm_message(self, document_data: Dict) -> str:
        """
        Build MDM^T02 (Document Notification) message
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        message_control_id = f"{timestamp}{document_data.get('patient_mrn', '')}"
        
        segments = []
        
        # MSH
        msh = (
            f"MSH|^~\\&|{self.sending_application}|{self.sending_facility}|"
            f"{self.receiving_application}|{self.receiving_facility}|"
            f"{timestamp}||MDM^T02|{message_control_id}|P|2.5"
        )
        segments.append(msh)
        
        # EVN
        evn = f"EVN|T02|{timestamp}"
        segments.append(evn)
        
        # PID
        pid = self._build_pid_segment(document_data.get('patient', {}))
        segments.append(pid)
        
        # TXA - Document Notification
        txa = self._build_txa_segment(document_data)
        segments.append(txa)
        
        # OBX - Document Content
        content = document_data.get('content', '')
        obx = f"OBX|1|TX|DOCUMENT||{content}"
        segments.append(obx)
        
        return '\r'.join(segments)
    
    def _build_txa_segment(self, document_data: Dict) -> str:
        """
        Build TXA segment
        """
        document_type = document_data.get('document_type', 'CN')
        document_id = document_data.get('document_id', '')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        txa = (
            f"TXA|1|{document_type}||{timestamp}|||{document_id}||||||"
            f"||||||AU"
        )
        
        return txa
    
    async def start_listener(self, port: int = 2575):
        """
        Start HL7 listener to receive incoming messages
        """
        async def handle_client(reader, writer):
            try:
                data = await reader.read(4096)
                
                if self.use_mllp:
                    message = data.decode('utf-8').strip('\x0b\x1c\x0d')
                else:
                    message = data.decode('utf-8')
                
                logger.info(f"Received HL7 message: {message[:100]}...")
                
                # Parse message type
                message_type = self._extract_message_type(message)
                
                # Call appropriate handler
                if message_type in self.message_handlers:
                    await self.message_handlers[message_type](message)
                
                # Send ACK
                ack = self._build_ack(message)
                
                if self.use_mllp:
                    ack_data = f"\x0b{ack}\x1c\x0d".encode('utf-8')
                else:
                    ack_data = ack.encode('utf-8')
                
                writer.write(ack_data)
                await writer.drain()
                
            except Exception as e:
                logger.error(f"Error handling HL7 message: {e}")
            finally:
                writer.close()
                await writer.wait_closed()
        
        server = await asyncio.start_server(handle_client, '0.0.0.0', port)
        logger.info(f"HL7 listener started on port {port}")
        
        self.listener_task = asyncio.create_task(server.serve_forever())
    
    def register_handler(self, message_type: str, handler: Callable):
        """
        Register a handler for a specific message type
        """
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")
    
    def _extract_message_type(self, message: str) -> str:
        """
        Extract message type from HL7 message
        """
        lines = message.split('\r')
        if lines:
            msh = lines[0]
            fields = msh.split('|')
            if len(fields) > 8:
                return fields[8]  # Message type field
        return ''
    
    def _build_ack(self, original_message: str) -> str:
        """
        Build ACK message
        """
        lines = original_message.split('\r')
        msh = lines[0]
        fields = msh.split('|')
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        message_control_id = fields[9] if len(fields) > 9 else timestamp
        
        ack_msh = (
            f"MSH|^~\\&|{self.sending_application}|{self.sending_facility}|"
            f"{fields[2]}|{fields[3]}|{timestamp}||ACK|{message_control_id}|P|2.5"
        )
        
        msa = f"MSA|AA|{message_control_id}"
        
        return f"{ack_msh}\r{msa}"
    
    async def stop_listener(self):
        """
        Stop HL7 listener
        """
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass
            logger.info("HL7 listener stopped")