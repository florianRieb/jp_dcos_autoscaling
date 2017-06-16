# autoscale.py

Wird für die automatische Skalierung der Anwendungen in Marathon genutzt.

Folgende Argumente mmüssen übergeben werden:

```
'--master', 'http://ip'        ->IP Adresse des Marathon Hosts

'--max_mem_percent', '30'      -> Maximale Memory Nutzung

'--max_cpu_time', '30'         -> Maximale CPU Nutzung

'--trigger_mode', 'or'         -> Müssen beide Schwellenwerte überschritten werden ('and') oder nur einer ('or')

'--autoscale_multiplier', '1.5'-> Für die Berechnung der Anzahl von Instancen z.B. 3 * 1.5 = 5 Instanzen (4,5 aufgerundet)

'--max_instances', '100'       -> Maximale Anzahl an Instanzen die nicht überschritten wird

'--marathon-app, 'nginx,nginx1'-> zu Überwachende App, bzw. Servicename von Marathon (kommaseparierte Liste)

'--min_instances', '1'         -> Minimale Anzahl an Instanzen

'--cool-down-factor', '5'      -> Messzyklen bis erneut herunter skaliert wird

'--trigger_number', '5'        -> Messzyklen bis erneut hoch (horizontal) skaliert wird

```

# Dockerfile
Um die Komponente im eigenen CLuster zu deployen muss ein eigenes Dockerfile erstellt und im marathon.json File
eingefügt werden. Denn wie im Pythin Skript zu sehen ist, wird das Token welches für den Zugriff auf die Marathon API
benötigt wird, aus einem externen Tokenfile gelesen. In diesem File wird lediglich in der ersten Zeile das Token abgelegt.

Da das hier verwendete Cluster nicht im Produktivbetrieb eingesetzt wird, wurde ein für mehrere Jahre gültiges Token erstellt.
https://medium.com/@richardgirges/authenticating-open-source-dc-os-with-third-party-services-125fa33a5add


# marathon-scale-app.json
Mit dem Label MARATHON_SINGLE_INSTANCE_APP :true wird gewährleistet, dass die Anwendung nur mit einer Instanz deployt
werden kann.



Diese Version ist nur für Testzwecke anzuwenden und basiert auf der Vorlage von:
https://github.com/mesosphere/marathon-autoscale

Verwendet für die Open DC/OS 1.9 Version.