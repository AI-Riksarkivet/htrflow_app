### Introduktion

Riksarkivet presenterar en demonstrationspipeline för HTR (Handwritten Text Recognition). Pipelinen består av två instanssegmenteringsmodeller: en tränad för att segmentera textregioner i bilder av löpande-textdokument och en annan tränad för att segmentera textrader inom dessa regioner. Textraderna transkriberas därefter av en textigenkänningsmodell som är tränad på ett stort dataset med svensk handskrift från 1600- till 1800-talet.

### Användning

Det är viktigt att betona att denna applikation främst är avsedd för demonstrationsändamål. Målet är att visa upp vår pipeline för att transkribera historiska dokument med löpande text, inte att använda pipelinen i storskalig produktion.  
**Obs**: I framtiden kommer vi att optimera koden för att passa ett produktionsscenario med multi-GPU och batch-inferens, men detta arbete pågår fortfarande. <br>

För en inblick i de kommande funktionerna vi arbetar med:

- Navigera till > **Översikt** > **Ändringslogg och roadmap**.

### Begränsningar

Demon, som är värd på Huggingface och tilldelad en T4 GPU, kan bara hantera två användarinlämningar åt gången. Om du upplever långa väntetider eller att applikationen inte svarar, är detta anledningen. I framtiden planerar vi att själva vara värdar för denna lösning, med en bättre server för en förbättrad användarupplevelse, optimerad kod och flera modellalternativ. Spännande utveckling är på gång!

Det är också viktigt att notera att modellerna fungerar på löpande text och inte text i tabellformat.
