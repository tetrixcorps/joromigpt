# Copyright(c) 2022-2024 NVIDIA Corporation. All rights reserved.

# NVIDIA Corporation and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA Corporation is strictly prohibited.

import os
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

config_file = "./env-config.js"

class AllowedTypes(Enum):
    STRING = 1
    NUMBER = 2
    BOOL = 3

env_variables = [
    [AllowedTypes.STRING, "UI_SERVER_ENDPOINT"], 
    [AllowedTypes.STRING, "WEBSOCKET_ENDPOINT"],
    [AllowedTypes.STRING, "VST_WEBSOCKET_ENDPOINT"],
    [AllowedTypes.BOOL, "ENABLE_INGRESS"],
    [AllowedTypes.BOOL, "ENABLE_CAMERA"],
    [AllowedTypes.STRING, "APP_TITLE"],
    [AllowedTypes.STRING, "APPLICATION_TYPE"],
    [AllowedTypes.BOOL, "OVERLAY_VISIBLE"],
    [AllowedTypes.BOOL, "UI_WINDOW_VISIBLE"],
    [AllowedTypes.BOOL, "TOP_BAR_VISIBLE"],
    [AllowedTypes.BOOL, "ASR_VISIBLE"],
    [AllowedTypes.BOOL, "TTS_VISIBLE"],
]

try:
    # Open in write mode to start fresh
    with open(config_file, 'w') as file:
        file.write("// Auto-generated environment configuration\n")
        
        for variable in env_variables:
            variable_type = variable[0]
            variable_name = variable[1]
            variable_value = os.getenv(variable_name)
            
            if variable_value:
                variable_value = variable_value.strip()
                
                try:
                    if variable_type == AllowedTypes.STRING:
                        if not (variable_value.startswith('"') and variable_value.endswith('"')):
                            override_js = f"const {variable_name} = \"{variable_value}\";\n"
                        else:
                            override_js = f"const {variable_name} = {variable_value};\n"
                            
                    elif variable_type == AllowedTypes.NUMBER:
                        try:
                            float(variable_value)  # Validate it's a number
                            override_js = f"const {variable_name} = {variable_value};\n"
                        except ValueError:
                            logger.warning(f"Invalid NUMBER value for {variable_name}: {variable_value}, skipping")
                            continue
                            
                    elif variable_type == AllowedTypes.BOOL:
                        if variable_value.lower() == "true":
                            override_js = f"const {variable_name} = true;\n"
                        elif variable_value.lower() == "false":
                            override_js = f"const {variable_name} = false;\n"
                        else:
                            logger.warning(f"Invalid BOOL value for {variable_name}: {variable_value}, skipping")
                            continue
                    else:
                        logger.warning(f"Unknown type for {variable_name}, skipping")
                        continue
                        
                    file.write(override_js)
                    logger.info(f"Added environment variable: {variable_name}")
                    
                except Exception as e:
                    logger.error(f"Error processing variable {variable_name}: {str(e)}")
                    
    logger.info(f"Environment configuration written to {config_file}")
    
except IOError as e:
    logger.error(f"Error writing to config file {config_file}: {str(e)}")