# autoscale.py

Wird für die automatische Skalierung der Anwendungen in Marathon genutzt.

Folgende Argumente mmüssen übergeben werden:

```
--master 'http://ip'        ->IP Adresse des Marathon Hosts

--max_mem_percent '30'      -> Maximale Memory Nutzung

--max_cpu_time '30'         -> Maximale CPU Nutzung

--trigger_mode 'or'         -> Müssen beide Schwellenwerte überschritten werden ('and') oder nur einer ('or')

--autoscale_multiplier '1.5'-> Für die Berechnung der Anzahl von Instancen z.B. 3 * 1.5 = 5 Instanzen (4,5 aufgerundet)

--max_instances '100'       -> Maximale Anzahl an Instanzen die nicht überschritten wird

--marathon-app 'nginx'      -> zu Überwachende App, bzw. Servicename von Marathon

--min_instances '1'         -> Minimale Anzahl an Instanzen

--cool-down-factor '5'      -> Messzyklen bis erneut herunter skaliert wird

--trigger_number '5'        -> Messzyklen bis erneut hoch (horizontal) skaliert wird

```


Diese Version ist nur für Testzwecke anzuwenden und basiert auf der Vorlage von:
https://github.com/mesosphere/marathon-autoscale

Verwendet für die Open DC/OS 1.9 Version.