/*
 * audio_processing.c
 *
 *  Created on: May 17, 2021
 *      Author: sydxrey
 *
 *
 * === Audio latency ===
 *
 * Receive DMA copies audio samples from the CODEC to the DMA buffer (through the I2S serial bus) as interleaved stereo samples
 * (either slots 0 and 2 for the violet on-board "LineIn" connector, or slots 1 and 3, for the pair of on-boards microphones).
 *
 * Transmit DMA copies audio samples from the DMA buffer to the CODEC again as interleaved stereo samples (in the present
 * implementation only copying to the headphone output, that is, to slots 0 and 2, is available).
 *
 * For both input and output transfers, audio double-buffering is simply implemented by using
 * a large (receive or transmit) buffer of size AUDIO_DMA_BUF_SIZE
 * and implementing half-buffer and full-buffer DMA callbacks:
 * - HAL_SAI_RxHalfCpltCallback() gets called whenever the receive (=input) buffer is half-full
 * - HAL_SAI_RxCpltCallback() gets called whenever the receive (=input) buffer is full
 *
 * As a result, one audio frame has a size of AUDIO_DMA_BUF_SIZE/2. But since one audio frame
 * contains interleaved L and R stereo samples, its true duration is AUDIO_DMA_BUF_SIZE/4.
 *
 * Example:
 * 		AUDIO_BUF_SIZE = 512 (=size of a stereo audio frame)
 * 		AUDIO_DMA_BUF_SIZE = 1024 (=size of the whole DMA buffer)
 * 		The duration of ONE audio frame is given by AUDIO_BUF_SIZE/2 = 256 samples, that is, 5.3ms at 48kHz.
 *
 * === interprocess communication ===
 *
 *  Communication b/w DMA IRQ Handlers and the main audio loop is carried out
 *  using the "audio_rec_buffer_state" global variable (using the input buffer instead of the output
 *  buffer is a matter of pure convenience, as both are filled at the same pace anyway).
 *
 *  This variable can take on three possible values:
 *  - BUFFER_OFFSET_NONE: initial buffer state at start-up, or buffer has just been transferred to/from DMA
 *  - BUFFER_OFFSET_HALF: first-half of the DMA buffer has just been filled
 *  - BUFFER_OFFSET_FULL: second-half of the DMA buffer has just been filled
 *
 *  The variable is written by HAL_SAI_RxHalfCpltCallback() and HAL_SAI_RxCpltCallback() audio in DMA transfer callbacks.
 *  It is read inside the main audio loop (see audioLoop()).
 *
 *  If RTOS is to used, Signals may be used to communicate between the DMA IRQ Handler and the main audio loop audioloop().
 *
 */

#include <audio.h>
#include <ui.h>
#include <stdio.h>
#include "string.h"
#include "math.h"
#include "bsp/disco_sai.h"
#include "bsp/disco_base.h"
#include "cmsis_os.h"

#include "arm_math.h"


extern SAI_HandleTypeDef hsai_BlockA2; // see main.c
extern SAI_HandleTypeDef hsai_BlockB2;
extern DMA_HandleTypeDef hdma_sai2_a;
extern DMA_HandleTypeDef hdma_sai2_b;


extern osThreadId defaultTaskHandle;
extern osThreadId uiTaskHandle;

// ---------- communication b/w DMA IRQ Handlers and the audio loop -------------

typedef enum {
	BUFFER_OFFSET_NONE = 0, BUFFER_OFFSET_HALF = 1, BUFFER_OFFSET_FULL = 2,
} BUFFER_StateTypeDef;
uint32_t audio_rec_buffer_state;




// ---------- DMA buffers ------------

// whole sample count in an audio frame: (beware: as they are interleaved stereo samples, true audio frame duration is given by AUDIO_BUF_SIZE/2)
#define AUDIO_BUF_SIZE   ((uint32_t)512)
/* size of a full DMA buffer made up of two half-buffers (aka double-buffering) */
#define AUDIO_DMA_BUF_SIZE   (2 * AUDIO_BUF_SIZE)

#define fftSize 128 //number of samples

// DMA buffers are in embedded RAM:
int16_t buf_input[AUDIO_DMA_BUF_SIZE];
int16_t buf_output[AUDIO_DMA_BUF_SIZE];
int16_t *buf_input_half = buf_input + AUDIO_DMA_BUF_SIZE / 2;
int16_t *buf_output_half = buf_output + AUDIO_DMA_BUF_SIZE / 2;
int posi = 0;
int deca=16000; //decalage en nombre d'echantillons



float32_t magFFt[fftSize/2]; //tableau comptenant la fft du signal en amplitude




arm_rfft_fast_instance_f32 fft;




// ------------- scratch float buffer for long delays, reverbs or long impulse response FIR based on float implementations ---------

uint32_t scratch_offset = 0; // see doc in processAudio()
#define AUDIO_SCRATCH_SIZE   AUDIO_SCRATCH_MAXSZ_WORDS



// ------------ Private Function Prototypes ------------

static void processAudio(int16_t*, int16_t*);
static void accumulateInputLevels();
static float readFloatFromSDRAM(int pos);
static void writeFloatToSDRAM(float val, int pos);

// ----------- Local vars ------------

//static int count = 0; // debug
//static double inputLevelL = 0;
//static double inputLevelR = 0;


static int count = 0;
static double inputLevelL = 0;
static double inputLevelR = 0;

// ----------- Functions ------------

/**
 * This is the main audio loop (aka infinite while loop) which is responsible for real time audio processing tasks:
 * - transferring recorded audio from the DMA buffer to buf_input[]
 * - processing audio samples and writing them to buf_output[]
 * - transferring processed samples back to the DMA buffer
 */
void audioLoop() {

	////uiDisplayBasic(); //affichage

	//AudioSetup();


	/* main audio loop */
	//while(1){

		/* Wait until first half block has been recorded */
		/*while (audio_rec_buffer_state != BUFFER_OFFSET_HALF) {
			asm("NOP");
		}
		audio_rec_buffer_state = BUFFER_OFFSET_NONE;
		*/

		/* Copy recorded 1st half block */
		osSignalSet(uiTaskHandle, 0x0001);
		osSignalWait (0x0001, osWaitForever);
		processAudio(buf_output, buf_input);
		osSignalSet(uiTaskHandle, 0x0001);


		/* Wait until second half block has been recorded */
		/*while (audio_rec_buffer_state != BUFFER_OFFSET_FULL) {
			asm("NOP");
		}


		audio_rec_buffer_state = BUFFER_OFFSET_NONE;
		 	 */
		osSignalWait (0x0001, osWaitForever);
		/* Copy recorded 2nd half block */
		processAudio(buf_output_half, buf_input_half);



	//}

}

void AudioSetup(){
	/* Initialize SDRAM buffers */
	memset((int16_t*) AUDIO_SCRATCH_ADDR, 0, AUDIO_SCRATCH_SIZE * 2); // note that the size argument here always refers to bytes whatever the data type

		audio_rec_buffer_state = BUFFER_OFFSET_NONE;

		// start SAI (audio) DMA transfers:
		startAudioDMA(buf_output, buf_input, AUDIO_DMA_BUF_SIZE);


		arm_rfft_fast_init_f32(&fft,fftSize);
}

void Graphique() {


		/* calculate average input level over 20 audio frames */

		accumulateInputLevels();

		count++;
		if (count >= 20) {
			count = 0;
			inputLevelL *= 0.05;
			inputLevelR *= 0.05;
			uiDisplayInputLevel(inputLevelL, inputLevelR);
			inputLevelL = 0.;
			inputLevelR = 0.;
		}

		DrawSprectrum();
}

int SizeScreenX = 480;

int SizeScreenY = 272;
static int x=10;
//int pas = SizeScreenY % fftSize;


void DrawSprectrum()
{

	//uiDisplayInputLevel((float)magFFt[1], 1);
	for(int y=0; y<fftSize/2;y++)
	{

		LCD_SetStrokeColor((int)(magFFt[y])*5);

		LCD_DrawPixel(x,y+128);

	}

	if(x<SizeScreenX){x +=1;}
	else{x =1;}

}





/*
 * Update input levels from the last audio frame (see global variable inputLevelL and inputLevelR).
 * Reminder: audio samples are actually interleaved L/R samples,
 * with left channel samples at even positions,
 * and right channel samples at odd positions.
 */
static void accumulateInputLevels() {

	// Left channel:
	uint32_t lvl = 0;
	for (int i = 0; i < AUDIO_DMA_BUF_SIZE; i += 2) {
		int16_t v = (int16_t) buf_input[i];
		if (v > 0)
			lvl += v;
		else
			lvl -= v;
	}
	inputLevelL += (double) lvl / AUDIO_DMA_BUF_SIZE / (1 << 15);

	// Right channel:
	lvl = 0;
	for (int i = 1; i < AUDIO_DMA_BUF_SIZE; i += 2) {
		int16_t v = (int16_t) buf_input[i];
		if (v > 0)
			lvl += v;
		else
			lvl -= v;
	}
	inputLevelR += (double) lvl / AUDIO_DMA_BUF_SIZE / (1 << 15);
	;
}

// --------------------------- Callbacks implementation ---------------------------

/**
 * Audio IN DMA Transfer complete interrupt.
 */


void HAL_SAI_RxCpltCallback(SAI_HandleTypeDef *hsai) {

	audio_rec_buffer_state = BUFFER_OFFSET_FULL;
	osSignalSet(defaultTaskHandle, 0x0001); //// si le buffer est plein on cherche ?? revenir au traitement audio
	return;
}

/**
 * Audio IN DMA Half Transfer complete interrupt.
 */
void HAL_SAI_RxHalfCpltCallback(SAI_HandleTypeDef *hsai) {

	//osSignalSet(uiTaskHandle, 0x0001);
	audio_rec_buffer_state = BUFFER_OFFSET_HALF;
	osSignalSet(defaultTaskHandle, 0x0001);

	return;
}

/* --------------------------- Audio "scratch" buffer in SDRAM ---------------------------
 *
 * The following functions allows you to use the external SDRAM as a "scratch" buffer.
 * There are around 7Mbytes of RAM available (~ 1' of stereo sound) which makes it possible to store signals
 * (either input or processed) over long periods of time for e.g. FIR filtering or long tail reverb's.
 */

/**
 * Read a 32 bit float from SDRAM at position "pos"
 */
static float readFloatFromSDRAM(int pos) {

	__IO float *pSdramAddress = (float*) AUDIO_SCRATCH_ADDR; // __IO is used to specify access to peripheral variables
	pSdramAddress += pos;
	//return *(__IO float*) pSdramAddress;
	return *pSdramAddress;

}

/**
 * Write the given 32 bit float to SDRAM at position "pos"
 */
static void writeFloatToSDRAM(float val, int pos) {

	__IO float *pSdramAddress = (float*) AUDIO_SCRATCH_ADDR;
	pSdramAddress += pos;
	//*(__IO float*) pSdramAddress = val;
	*pSdramAddress = val;


}

/**
 * Read a 16 bit integer from SDRAM at position "pos"
 */
static int16_t readInt16FromSDRAM(int pos) {

	__IO int16_t *pSdramAddress = (int16_t*) AUDIO_SCRATCH_ADDR;
	pSdramAddress += pos;
	//return *(__IO int16_t*) pSdramAddress;
	return *pSdramAddress;

}

/**
 * Write the given 16 bit integer to the SDRAM at position "pos"
 */
static void writeInt16ToSDRAM(int16_t val, int pos) {

	__IO int16_t *pSdramAddress = (int16_t*) AUDIO_SCRATCH_ADDR;
	pSdramAddress += pos;
	//*(__IO int16_t*) pSdramAddress = val;
	*pSdramAddress = val;

}

// --------------------------- AUDIO ALGORITHMS ---------------------------

/**
 * This function is called every time an audio frame
 * has been filled by the DMA, that is,  AUDIO_BUF_SIZE samples
 * have just been transferred from the CODEC
 * (keep in mind that this number represents interleaved L and R samples,
 * hence the true corresponding duration of this audio frame is AUDIO_BUF_SIZE/2 divided by the sampling frequency).
 */

float seuil1=0;
float seuil2 = 0.39;
float gainTan = 0;
float p1 = 1.4;
#define  p2  (1-(p1*(seuil2-seuil1)+gainTan))/(1-seuil2)


int reverb1=4571;
int reverb2=4971;
int reverb3=5371;
int reverb4=5771;



static void processAudio(int16_t *out, int16_t *in) {

	LED_On(); // for oscilloscope measurements...



// echo
	//int NumberBufSave =100;

		for (int n = 0; n < AUDIO_BUF_SIZE; n++){
			posi=posi+1;

			//compression
			if(in[n]<=seuil1 && in[n]>=-seuil1){in[n]=gainTan*tan(in[n]*3.1415/(4*seuil1));}
			else if(in[n]>=seuil1 && in[n]<=seuil2) {in[n]=p1*(in[n]-seuil1)+gainTan;}
			else if(in[n]<=-seuil1 && in[n]>=-seuil2) {in[n]=p1*(in[n]+seuil1)-gainTan;}

			else if(in[n]>=seuil2) {in[n]=p2*(in[n]-seuil2)+gainTan+p1*(seuil2-seuil1);}
			else if(in[n]<=-seuil2) {in[n]=p2*(in[n]+seuil2)+gainTan-p1*(seuil2-seuil1);}

			//compression(in, n);



			//________________________

			writeInt16ToSDRAM(in[n], posi);

			if(posi>=deca)
			{ //out[n]= 0.5*readInt16FromSDRAM(posi-deca)+readInt16FromSDRAM(posi); //echo
				out[n]= 0.25*readInt16FromSDRAM(posi-reverb1)+0.12*readInt16FromSDRAM(posi-reverb2)+0.06*readInt16FromSDRAM(posi-reverb3)+0.03*readInt16FromSDRAM(posi-reverb4)+0.5*readInt16FromSDRAM(posi);




			}

			else {out[n] = readInt16FromSDRAM(posi);}


			if(posi>100000)
			 {posi=0;}


			//out[n] = in[n-nu];
		}

		if((posi%fftSize ==0)&& (posi>fftSize)){
			uiDisplayInputLevel(1, posi);

		}
		runFFT();


//	out[n] = in[n];

	LED_Off();
}






void runFFT()
{
	//int32_t startTime, stopTime, totalTime;


	float32_t inputData[fftSize];
	float32_t rfftOutput[fftSize];
	for(int i=0;i<fftSize;i++)
	{

		inputData[i]= (float32_t)readInt16FromSDRAM(posi-(fftSize*2)+i*2);
	}




	//float32_t maxValue;
	uint8_t rfftFlag=0;

	// Setup timer
	// This is just used for timing during test!!
//	ROM_SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0);
//	ROM_TimerConfigure(TIMER0_BASE, TIMER_CFG_PERIODIC);
//	ROM_TimerLoadSet(TIMER0_BASE, TIMER_A, g_ui32SysClock); // 1 second

	// Create a RFFT instance

	//arm_rfft_fast_instance_f32 fft;
	//arm_rfft_fast_init_f32(&fft,fftSize);


	// Run FFT
//	ROM_TimerEnable(TIMER0_BASE, TIMER_A);
//	startTime = TIMER0_TAR_R;
	/*
	 void arm_rfft_fast_f32(
	 arm_rfft_fast_instance_f32 * S,
	 float32_t * p, float32_t * pOut,
	 uint8_t ifftFlag);*/

	/* Process the real data through the RFFT module */
	arm_rfft_fast_f32(&fft, inputData, rfftOutput, rfftFlag);

	/* Process the data through the Complex Magnitude Module for
	  calculating the magnitude at each bin */
	//arm_cmplx_mag_f32(rfftOutput, magFFt, fftSize / 2);
	arm_cmplx_mag_f32(rfftOutput, magFFt, fftSize/2);






	//MAP_SysCtlDelay(1);


}







void compression(int16_t *in, int n){


	if(in[n]<=seuil1 && in[n]>=-seuil1){in[n]=gainTan*tan(in[n]*3.1415/(4*seuil1));}
	else if(in[n]>=seuil1 && in[n]<=seuil2) {in[n]=p1*(in[n]-seuil1)+gainTan;}
	else if(in[n]<=-seuil1 && in[n]>=-seuil2) {in[n]=p1*(in[n]+seuil1)-gainTan;}

	else if(in[n]>=seuil2) {in[n]=p2*(in[n]-seuil2)+gainTan+p1*(seuil2-seuil1);}
	else if(in[n]<=-seuil2) {in[n]=p2*(in[n]+seuil2)+gainTan-p1*(seuil2-seuil1);}

}




