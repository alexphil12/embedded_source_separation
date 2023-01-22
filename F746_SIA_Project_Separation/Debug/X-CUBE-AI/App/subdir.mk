################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (10.3-2021.10)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../X-CUBE-AI/App/network_1.c \
../X-CUBE-AI/App/network_1_data.c \
../X-CUBE-AI/App/network_1_data_params.c 

OBJS += \
./X-CUBE-AI/App/network_1.o \
./X-CUBE-AI/App/network_1_data.o \
./X-CUBE-AI/App/network_1_data_params.o 

C_DEPS += \
./X-CUBE-AI/App/network_1.d \
./X-CUBE-AI/App/network_1_data.d \
./X-CUBE-AI/App/network_1_data_params.d 


# Each subdirectory must supply rules for building sources it contributes
X-CUBE-AI/App/%.o X-CUBE-AI/App/%.su: ../X-CUBE-AI/App/%.c X-CUBE-AI/App/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m7 -std=gnu11 -g3 -DARM_MATH_CM7 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F746xx -c -I../Core/Inc -I../FATFS/Target -I../FATFS/App -I../USB_HOST/App -I../USB_HOST/Target -I../Drivers/STM32F7xx_HAL_Driver/Inc -I../Drivers/STM32F7xx_HAL_Driver/Inc/Legacy -I../Middlewares/Third_Party/FreeRTOS/Source/include -I../Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS -I../Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM7/r0p1 -I../Middlewares/Third_Party/FatFs/src -I../Middlewares/ST/STM32_USB_Host_Library/Core/Inc -I../Middlewares/ST/STM32_USB_Host_Library/Class/CDC/Inc -I../Drivers/CMSIS/Device/ST/STM32F7xx/Include -I../Drivers/CMSIS/Include -I../LIBJPEG/App -I../LIBJPEG/Target -I../Middlewares/Third_Party/LibJPEG/include -I../Drivers/CMSIS/DSP/Include -I../Middlewares/ST/AI/Inc -I../X-CUBE-AI/App -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv5-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-X-2d-CUBE-2d-AI-2f-App

clean-X-2d-CUBE-2d-AI-2f-App:
	-$(RM) ./X-CUBE-AI/App/network_1.d ./X-CUBE-AI/App/network_1.o ./X-CUBE-AI/App/network_1.su ./X-CUBE-AI/App/network_1_data.d ./X-CUBE-AI/App/network_1_data.o ./X-CUBE-AI/App/network_1_data.su ./X-CUBE-AI/App/network_1_data_params.d ./X-CUBE-AI/App/network_1_data_params.o ./X-CUBE-AI/App/network_1_data_params.su

.PHONY: clean-X-2d-CUBE-2d-AI-2f-App

