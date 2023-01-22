/*
 * audio_processing.h
 *
 *  Created on: May 17, 2021
 *      Author: sydxrey
 */

#ifndef INC_AUDIO_H_
#define INC_AUDIO_H_

#include "stdint.h"

void audioLoop();
void Graphique();
void AudioSetup();
void runFFT();
void DrawSprectrum();

void compression(int16_t *in, int n);
#endif /* INC_AUDIO_H_ */
