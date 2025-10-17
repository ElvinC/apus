/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2023 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32wlxx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
//#include "eeprom_emul.h"
/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);
void MX_SUBGHZ_Init(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define BUZZER_Pin GPIO_PIN_8
#define BUZZER_GPIO_Port GPIOA
#define LED_Pin GPIO_PIN_9
#define LED_GPIO_Port GPIOA
#define BOOT_Pin GPIO_PIN_3
#define BOOT_GPIO_Port GPIOH
#define CS_FLASH_Pin GPIO_PIN_10
#define CS_FLASH_GPIO_Port GPIOA
#define CS_IMU_Pin GPIO_PIN_13
#define CS_IMU_GPIO_Port GPIOA
#define CS_BARO_Pin GPIO_PIN_13
#define CS_BARO_GPIO_Port GPIOC
#define PYRO2_CON_Pin GPIO_PIN_14
#define PYRO2_CON_GPIO_Port GPIOC
#define PYRO1_CON_Pin GPIO_PIN_15
#define PYRO1_CON_GPIO_Port GPIOC
#define PYRO2_Pin GPIO_PIN_14
#define PYRO2_GPIO_Port GPIOA
#define PYRO1_Pin GPIO_PIN_15
#define PYRO1_GPIO_Port GPIOA

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
