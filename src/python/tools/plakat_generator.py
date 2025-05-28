"""
Plakat Generator Tool - Pure Python Implementation

This tool generates PDF posters using the same logic as the plakat_gen application,
but implemented purely in Python without Node.js dependencies.

Based on: /root/vyvoj_sw/plakat_gen backend functionality

Author: Generated with Claude Code
"""

import requests
import time
import os
import tempfile
import base64
from typing import Dict, List, Any, Optional, Tuple
from .base_tool import BaseTool


class PlakatGenerator(BaseTool):
    """Generator for PDF posters using direct HTTP requests to external service"""
    
    def __init__(self, logger=None):
        super().__init__(logger)
        self.external_service_url = "https://publicita.dotaceeu.cz/gen/krok1"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        self.step_delay = 500  # milliseconds
        self.timeout = 60000  # milliseconds
        
    def validate_inputs(self, files: List[str], options: Dict[str, Any]) -> bool:
        """Validate input options for plakat generation"""
        required_keys = ['projects', 'orientation', 'common_text']
        
        for key in required_keys:
            if key not in options:
                self.errors.append(f"Chybí povinný parametr: {key}")
                return False
        
        projects = options['projects']
        if not isinstance(projects, list) or not projects:
            self.errors.append("Projekty musí být neprázdný seznam")
            return False
        
        for i, project in enumerate(projects):
            if not isinstance(project, dict) or 'id' not in project or 'name' not in project:
                self.errors.append(f"Projekt {i+1} musí obsahovat 'id' a 'name'")
                return False
        
        orientation = options['orientation']
        if orientation not in ['portrait', 'landscape']:
            self.errors.append("Orientace musí být 'portrait' nebo 'landscape'")
            return False
        
        common_text = options['common_text']
        if not isinstance(common_text, str) or len(common_text) > 255:
            self.errors.append("Společný text musí být string s max. 255 znaky")
            return False
        
        return True
    
    def _delay(self, ms: int):
        """Wait for specified milliseconds"""
        time.sleep(ms / 1000.0)
    
    def _debug_step_progress(self, soup, context: str):
        """Debug step progress by checking classes"""
        steps = soup.find('ul', {'id': 'steps'})
        if steps:
            step_items = steps.find_all('li')
            status = []
            for i, item in enumerate(step_items, 1):
                classes = item.get('class', [])
                if 'done' in classes:
                    status.append(f"Step{i}:DONE")
                elif 'active' in classes:
                    status.append(f"Step{i}:ACTIVE")
                else:
                    status.append(f"Step{i}:PENDING")
            self.logger.info(f"{context} - Progress: {' | '.join(status)}")
        else:
            self.logger.warning(f"{context} - No steps element found")
    
    def _step1_initialize_session(self, session: requests.Session) -> Dict[str, str]:
        """Initialize session and get initial tokens"""
        self.logger.info("Step 1: Initializing session")
        
        response = session.get(
            self.external_service_url,
            headers={'User-Agent': self.user_agent},
            timeout=self.timeout / 1000
        )
        response.raise_for_status()
        
        # Extract PHPSESSID from cookies
        phpsessid = session.cookies.get('PHPSESSID')
        if not phpsessid:
            raise Exception("Failed to get PHPSESSID")
        
        # Extract form token from HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: Check initial step progress
        self._debug_step_progress(soup, "After step 1 (init)")
        
        token_input = soup.find('input', {'name': 'form[_token]'})
        if not token_input:
            raise Exception("Failed to get initial token")
        
        current_token = token_input.get('value')
        
        return {
            'phpsessid': phpsessid,
            'current_token': current_token
        }
    
    def _step2_set_format(self, session: requests.Session, session_data: Dict[str, str], orientation: str):
        """Set poster format (orientation)"""
        self.logger.info("Step 2: Setting poster format")
        
        format_value = "7" if orientation == "landscape" else "6"  # 6=A4 na výšku, 7=A4 na šířku
        
        form_data = {
            'form[_token]': session_data['current_token'],
            'form[format]': format_value
        }
        
        response = session.post(
            self.external_service_url,  # POST back to krok1
            data=form_data,
            headers={'User-Agent': self.user_agent},
            timeout=self.timeout / 1000
        )
        response.raise_for_status()
        
        # Update token from response and check progress
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: Check step progress after format selection
        self._debug_step_progress(soup, "After step 2 (format)")
        
        token_input = soup.find('input', {'name': 'form[_token]'})
        if token_input:
            session_data['current_token'] = token_input.get('value')
    
    def _step3_send_project_data(self, session: requests.Session, session_data: Dict[str, str], 
                                project: Dict[str, str], common_text: str):
        """Send project data to the service"""
        self.logger.info(f"Step 3: Sending project data for {project['id']}")
        
        project_text = f"{project['id']} - {project['name']}"
        target_html = f"<p>{common_text}</p>"
        
        form_data = {
            'form[_token]': session_data['current_token'],
            'form[texts][0][program]': '2',
            'form[texts][0][project]': project_text,
            'form[texts][0][target]': target_html,
            'form[texts][0][rowCount]': '1',
            'form[texts][0][charCount]': str(len(target_html)),  # Count characters in target, not project
            'form[texts][0][financingType]': 'co-financed',  # Correct value from your spec
            'form[texts][0][financingTypeTextTense]': 'present',
            'form[texts][0][logoImage]': '',
            'files[]': ''
        }
        
        # Add proper headers including Content-Type
        headers = {
            'User-Agent': self.user_agent,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive'
        }
        
        response = session.post(
            "https://publicita.dotaceeu.cz/gen/krok2",
            data=form_data,
            headers=headers,
            timeout=self.timeout / 1000
        )
        response.raise_for_status()
        
        # Update token from response and check progress
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: Check step progress after project data
        self._debug_step_progress(soup, "After step 3 (project data)")
        
        token_input = soup.find('input', {'name': 'form[_token]'})
        if token_input:
            session_data['current_token'] = token_input.get('value')
    
    def _step4_finalize(self, session: requests.Session, session_data: Dict[str, str]):
        """Finalize generation (set cropmarks)"""
        self.logger.info("Step 4: Finalizing generation")
        
        # Try different cropmarks field names
        form_data = {
            'form[_token]': session_data['current_token'],
            'form[cropmarks]': '0',  # 0 = no cropmarks
            'form[orizavaciZnacky]': '0',  # Try Czech name
            'cropmarks': '0'  # Try simple name
        }
        
        response = session.post(
            "https://publicita.dotaceeu.cz/gen/krok3",
            data=form_data,
            headers={'User-Agent': self.user_agent},
            timeout=self.timeout / 1000
        )
        response.raise_for_status()
        
        # Update token from response and check progress
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: Check step progress after cropmarks
        self._debug_step_progress(soup, "After step 4 (cropmarks)")
        
        token_input = soup.find('input', {'name': 'form[_token]'})
        if token_input:
            session_data['current_token'] = token_input.get('value')
    
    def _step5_download_pdf(self, session: requests.Session, session_data: Dict[str, str]) -> bytes:
        """Download the generated PDF"""
        self.logger.info("Step 5: Downloading PDF from /gen/nahled")
        
        # Direct GET to nahled - server should return PDF
        response = session.get(
            "https://publicita.dotaceeu.cz/gen/nahled",
            headers={
                'User-Agent': self.user_agent,
                'Connection': 'keep-alive',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
            },
            timeout=self.timeout / 1000
        )
        
        self.logger.info(f"Response status: {response.status_code}, Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        # Check if response is PDF
        if response.status_code == 200 and response.headers.get('content-type', '').startswith('application/pdf'):
            self.logger.info("Got PDF directly from server")
            return response.content
        else:
            # Log response details for debugging
            self.logger.error(f"Unexpected response: Status={response.status_code}, Headers={dict(response.headers)}")
            if response.status_code == 500:
                raise Exception(f"Server error 500 - možná chybí session context nebo je problém na serveru")
            else:
                raise Exception(f"Expected PDF but got {response.headers.get('content-type', 'unknown')}")
    
    def _generate_poster_for_project(self, project: Dict[str, str], orientation: str, common_text: str) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """Generate poster for a single project"""
        try:
            self.logger.info(f"Generating poster for project: {project['id']}")
            
            # Create session with cookies
            session = requests.Session()
            session.headers.update({
                'User-Agent': self.user_agent,
                'Connection': 'keep-alive'
            })
            
            # Step 1: Initialize session
            session_data = self._step1_initialize_session(session)
            
            # Step 2: Set format
            self._delay(self.step_delay)
            self._step2_set_format(session, session_data, orientation)
            
            # Step 3: Send project data
            self._delay(self.step_delay)
            self._step3_send_project_data(session, session_data, project, common_text)
            
            # Step 4: Finalize
            self._delay(self.step_delay)
            self._step4_finalize(session, session_data)
            
            # Step 5: Download PDF
            self._delay(self.step_delay)
            pdf_content = self._step5_download_pdf(session, session_data)
            
            # Generate filename
            filename = self._generate_filename(project['id'])
            
            self.logger.info(f"Successfully generated poster for project: {project['id']}")
            return True, pdf_content, filename
            
        except Exception as e:
            self.logger.error(f"Failed to generate poster for project {project['id']}: {str(e)}")
            return False, None, str(e)
    
    def _generate_filename(self, project_id: str) -> str:
        """Generate filename from project ID"""
        # Extract last digits from project ID for filename
        digits = ''.join(filter(str.isdigit, project_id))
        if len(digits) >= 3:
            suffix = digits[-3:]
        else:
            suffix = digits or "000"
        
        return f"plakat_{suffix}.pdf"
    
    def process(self, files: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """Process poster generation request"""
        try:
            # Validate input
            if not self.validate_inputs(files, options):
                return {
                    'success': False, 
                    'errors': self.errors,
                    'warnings': self.warnings,
                    'info': self.info_messages
                }
            
            projects = options['projects']
            orientation = options['orientation']
            common_text = options['common_text']
            output_dir = options.get('output_dir', tempfile.mkdtemp())
            
            self.logger.info(f"Starting poster generation for {len(projects)} projects")
            
            successful_projects = 0
            failed_projects = 0
            saved_files = []
            
            # Process each project
            for i, project in enumerate(projects):
                self.logger.info(f"Processing project {i+1}/{len(projects)}: {project['id']}")
                
                try:
                    success, pdf_content, filename_or_error = self._generate_poster_for_project(
                        project, orientation, common_text
                    )
                    
                    if success and pdf_content:
                        # Save PDF file
                        file_path = os.path.join(output_dir, filename_or_error)
                        with open(file_path, 'wb') as f:
                            f.write(pdf_content)
                        
                        saved_files.append(file_path)
                        successful_projects += 1
                        self.info_messages.append(f"Saved: {filename_or_error}")
                        
                    else:
                        failed_projects += 1
                        error_msg = f"Project {project['id']}: {filename_or_error}"
                        self.errors.append(error_msg)
                    
                    # Delay between projects (except for the last one)
                    if i < len(projects) - 1:
                        delay_ms = 3000 + (2000 * (i % 3))  # Varying delays
                        self.logger.info(f"Waiting {delay_ms}ms before next project...")
                        self._delay(delay_ms)
                        
                except Exception as e:
                    failed_projects += 1
                    error_msg = f"Project {project['id']}: Unexpected error - {str(e)}"
                    self.errors.append(error_msg)
            
            # Generate summary
            total_projects = len(projects)
            if successful_projects > 0:
                summary = f"Vygenerováno {successful_projects} plakátů z {total_projects}"
                if failed_projects > 0:
                    summary += f" ({failed_projects} selhalo)"
                
                return {
                    'success': True,
                    'message': summary,
                    'data': {
                        'successful_projects': successful_projects,
                        'failed_projects': failed_projects,
                        'total_projects': total_projects,
                        'output_files': saved_files
                    },
                    'errors': self.errors,
                    'warnings': self.warnings,
                    'info': self.info_messages
                }
            else:
                return {
                    'success': False,
                    'message': f"Generování všech {total_projects} plakátů selhalo",
                    'data': {
                        'successful_projects': 0,
                        'failed_projects': failed_projects,
                        'total_projects': total_projects,
                        'output_files': []
                    },
                    'errors': self.errors,
                    'warnings': self.warnings,
                    'info': self.info_messages
                }
                
        except Exception as e:
            self.logger.error(f"Unexpected error in poster generation: {str(e)}")
            self.errors.append(f"Neočekávaná chyba: {str(e)}")
            return {
                'success': False,
                'errors': self.errors,
                'warnings': self.warnings,
                'info': self.info_messages
            }