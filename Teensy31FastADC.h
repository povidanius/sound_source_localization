//FAST 8 BIT SETUP AND READING FOR 2 ADCs
//THIS IS TEENSY VERSION 3.1 SPECIFIC

#ifndef _teensy31adc_h_
#define _teensy31adc_h_

#include <ADC.h>


//defined as a macro its faster
#define highSpeed8bitAnalogReadMacro(channel1, channel2, value1, value2) ADC0_SC1A = channel1;ADC1_SC1A = channel2;while (!(ADC0_SC1A & ADC1_SC1A & ADC_SC1_COCO)) {} value1 = ADC0_RA;value2 = ADC1_RA;

/*
FUNCTION PSEUDOCODE FOR MACRO, of course we could not pass value1 and value2 like this to a function (should be pointers or return a struct)
int highSpeed8bitAnalogRead(uint8_t channel1, uint8_t channel2, int value1, int value2){
        ADC0_SC1A = channel1;
        ADC1_SC1A = channel2;
        while (!(ADC0_SC1A & ADC1_SC1A & ADC_SC1_COCO)) {}
	value1 = ADC0_RA;
	value2 = ADC1_RA;
}
*/


void highSpeed8bitADCSetup(){
  
  /*
      0 ADLPC (Low-Power Configuration)
      0 ADIV (Clock Divide Select)
      0
      0 ADLSMP (Sample time configuration)
      0 MODE (Conversion mode selection) (00=8/9, 01=12/13, 10=10/11, 11=16/16 bit; diff=0/1)
      0
      0 ADICLK (Input Clock Select)
      0
  */
  ADC0_CFG1 = 0b00000000;
  ADC1_CFG1 = 0b00000000;

   /*
      0 MUXSEL (ADC Mux Select)
      0 ADACKEN (Asynchrononous Clock Output Enable)
      0 ADHSC (High-Speed Configuration)
      0 ADLSTS (Long Sample Time Select) (00=+20 cycles, 01=+12, 10=+6, 11=+2)
      0
  */
  ADC0_CFG2 = 0b00010100;
  ADC1_CFG2 = 0b00010100;
  
  /*
      0 ADTRG (Conversion Trigger Select)
      0 ACFE (Compare Function Enable)
      0 ACFGT (Compare Function Greater than Enable)
      0 ACREN (Compare Function Range Enable)
      0 ACREN (COmpare Function Range Enable)
      0 DMAEN (DMA Enable)
      0 REFSEL (Voltage Reference Selection) (00=default,01=alternate,10=reserved,11=reserved)
  */
  ADC0_SC2 = 0b00000000;
  ADC1_SC2 = 0b00000000;
 
  /*
      1 CAL (Calibration)
      0 CALF (read only)
      0 (Reserved)
      0
      0 ADCO (Continuous Conversion Enable)
      1 AVGS (Hardware Average Enable)
      1 AVGS (Hardware Average Select) (00=4 times, 01=8, 10=16, 11=32)
      1
  */
  
  ADC0_SC3 = 0b10000000;
  ADC1_SC3 = 0b10000000;

  
  // Waiting for calibration to finish. The documentation is confused as to what flag to be waiting for (SC3[CAL] on page 663 and SC1n[COCO] on page 687+688).
  while (ADC0_SC3 & ADC_SC3_CAL) {} ;
  while (ADC1_SC3 & ADC_SC3_CAL) {} ;

}

#endif
