# Neuro3D: candidate experimental partners for a small optical demonstrator

Prepared 2026-10-13 by Claude (research only). **Nothing has been sent.** No one was contacted, no form was submitted and no account was created. Everything below comes from public web pages checked on 2026-10-13.

## 1. Purpose

Neuro3D (github.com/Agnuxo1/Neuro3D, Francisco Angulo de Lafuente, independent researcher, Spain) is a coherent scalar optical neural-network simulator. Its fields and trainable phases come from Blender 3D geometry, and its numerics are certified. All results so far are simulator results; there is no physical device yet. The guide sets out a physical ladder (D0-B):

1. A Mach-Zehnder interferometer (MZI) with measured visibility and phase stability.
2. A reconfigurable 2x2 network with transfer-matrix tomography.
3. A small network reproduced from a captured scene.
4. A 5-input, 8-output network.

Platforms, from cheapest to most expensive: free-space optics with commercial parts; fiber couplers and phase shifters; integrated photonics through multi-project wafers (MPW) with a partner. Predictions and their uncertainty are published before each measurement, and the partner supplies the measurement record.

## 2. Selection criteria

- **Ladder fit.** The group can plausibly measure step 1 or 2 cheaply (free-space or fiber MZI, 2x2 tomography) or offer a route to steps 3-4 (SLM or diffractive phase reproduction, programmable meshes, MPW).
- **Topic fit.** Optical neural networks, programmable photonic meshes, diffractive or free-space optical computing, photonic reservoir computing, or SLM-based computational optics.
- **Proximity and cost.** Spain first, then Europe, then elsewhere. Low-cost, short asks are preferred.
- **Verifiability.** Each entry was checked against at least one live public page. PIs are named only when a public page names them. Emails are listed only when they are generic (institutional or info addresses) and shown on the page; personal addresses that appear on lab pages are left out on purpose.
- **Fit score (1-5)** measures scientific and practical fit for the ask. It does **not** predict whether anyone will reply.

## 3. Candidate table (25 entries)

Abbreviations: FS = free-space; SLM = spatial light modulator; PIC = photonic integrated circuit; SOI = silicon-on-insulator.

### 3a. Spain

| # | Group / lab | Institution | Country | PI / head (public) | Ladder step: why it fits | Platform | Public contact route | Verified on (live page) | Fit |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Photonics Research Labs (PRL), iTEAM | Universitat Politècnica de València (UPV) | ES | José Capmany (Full Professor, listed on team page; press names him as PRL head) | **2, 4**: an international reference in programmable photonics (MZI-based meshes, a Nature review with D. Pérez). A 2x2 programmable cell with tomography is their everyday work. | PIC (programmable SOI meshes), fiber | https://www.prl.upv.es/contact/ | https://www.prl.upv.es/prl-group/team/ ; https://www.upv.es/noticias-upv/noticia-12342-la-upv-referen-es.html | **5**: closest topical match in Spain. |
| 2 | Nanophotonics Technology Center (NTC) | UPV | ES | Director not named on the page checked (*uncertain*) | **4**: 500 m² cleanroom, part of the Micronanofabs ICTS (a Spanish national infrastructure), offers fabrication and characterization services. | PIC (silicon) fabrication and testing | Generic: info-ntc@upv.es | https://ntc.webs.upv.es/the-institute/ | **3**: a service route for later steps; paid access is likely. |
| 3 | Nonlinear Photonics Lab / FoCo-SiNeu (Complex Photonics and Neuro-inspired Systems) | IFISC (UIB-CSIC), Palma | ES | Ingo Fischer | **1-2**: photonic information processing and reservoir computing with lasers and delay systems; strong measurement culture (stability, noise). | FS / fiber / semiconductor lasers | Generic: ifisc@ifisc.uib-csic.es | https://ifisc.uib-csic.es/ingo/main.html (dated 2017) ; https://portalinvestigacio.uib.cat/investigadores/1982300/detalle?lang=en | **4**: neuromorphic photonics in Spain; the lab page is old, so check current focus. |
| 4 | GROC·UJI (Optics Research Group) | Universitat Jaume I, Castellón | ES | María Gladis Mínguez Vega; Enrique Tajahuerce (leaders per university portal) | **1, 3**: computational optics with megapixel SLMs and digital beam control. Could encode a Neuro3D phase screen on an SLM and measure it. | FS + SLM | Group page: https://www.uji.es/serveis/ocit/base/grupsinvestigacio/detall?codi=087 | https://portalcientific.uji.es/grupos/199701/detalle?lang=en | **4**: SLM reproduction of a captured-scene phase is a natural step 3. |
| 5 | TecnOPTO (Optical and Optoelectronic Technologies) | Universidad Miguel Hernández, Elche | ES | Ignacio Moreno (leads TecnOPTO per UMH pages; the homepage lists members only) | **1, 3**: liquid-crystal SLMs, structured light, polarization and diffractive optics. Moreno's PhD was on an SLM programmable optical correlator. | FS + SLM, polarization | https://tecnopto.umh.es/ (no email shown) | https://tecnopto.umh.es/ ; https://tecnopto.umh.es/materiales/ignacio-moreno/ | **4**: cheap FS MZI/SLM expertise; Moreno is EOS President-Elect (per search snippet, *unverified*). |
| 6 | Grupo de Holografía y Procesado Óptico (GHPO) | Universidad de Alicante | ES | Augusto Beléndez Vázquez; M. Inmaculada Pascual Villalobos (directors) | **1, 3**: holographic optical elements, photopolymers, LC-SLMs. Could fabricate a static diffractive element from a Neuro3D phase map. | FS, holographic elements | https://web.ua.es/es/ghpo/grupo-de-holografia-y-procesado-optico_contactar.html | https://web.ua.es/es/ghpo/ | **3**: good for static-element reproduction; less focus on computing. |
| 7 | Diffractive Optics Group (DiOG) | UPV + Universitat de València | ES | Not named on the homepage; UV pages list W. D. Furlan as co-director (*verify*) | **3**: design and characterization of diffractive optical elements and optical encryption. | FS diffractive optics | http://diog.webs.upv.es (contact section on site) | https://diog.webs.upv.es/ | **3**: diffractive-element know-how, ophthalmic focus. |
| 8 | Applied Optics Complutense Group (AOCG) | Universidad Complutense de Madrid | ES | Javier Alda (director); Luis Miguel Sánchez-Brea (co-director) | **1**: optical metrology, computational tools for optics, micro-optics. Can quantify visibility and phase stability rigorously. | FS metrology | https://ucm.es/aocg (directors' personal emails on page, not reproduced) | https://ucm.es/aocg | **3**: solid metrology partner; no optical-computing line. |
| 9 | Optoelectronics group | ICFO, Castelldefels | ES | Valerio Pruneri (ICREA Prof., Corning Inc. Chair) | **1-2**: integrated modulators, fiber optics, interferometric and quantum phase imagers; strong industry links. | Fiber / FS / devices | https://icfo.eu/about-icfo/people/directory/?id=153 | https://www.icrea.cat/community/icreas/17526/valerio-pruneri | **3**: capable, but a small unfunded ask is unlikely to be a priority. |
| 10 | Photonics & RF Research Lab (TELMA) | Universidad de Málaga | ES | Iñigo Molina-Fernández (leader per search results, *partly verified*); Robert Halir (verified on university portal) | **2, 4**: SOI couplers, MMIs, metamaterial waveguides; designs and characterizes MZI-type circuits. | PIC (SOI) | https://www.photonics-rf.uma.es (TLS certificate error on fetch) | https://portaldelainvestigacion.uma.es/investigadores/1240197/detalle?lang=en | **4**: strong Spanish PIC design and measurement group. |

### 3b. Rest of Europe

| # | Group / lab | Institution | Country | PI / head (public) | Ladder step: why it fits | Platform | Public contact route | Verified on (live page) | Fit |
|---|---|---|---|---|---|---|---|---|---|
| 11 | Photonics Research Group (with imec) | Ghent University | BE | Peter Bienstman (photonic reservoir computing / unconventional processing); Wim Bogaerts (programmable photonics, *from third-party pages*) | **2, 4**: passive photonic reservoirs and programmable silicon circuits; close to imec MPW. | PIC (SOI) | https://www.photonics.intec.ugent.be/ (People page 404 at check time) | https://www.photonics.intec.ugent.be/ ; https://www.optica.org/events/webinar/2025/06_june/unconventional_photonic_information_processing_using_silicon_photonics | **5**: neuromorphic plus programmable photonics in one group. |
| 12 | Photonic Devices Group / Lab (PoliFAB) | Politecnico di Milano (DEIB) | IT | Andrea Melloni (contact on page); Francesco Morichetti | **2, 4**: programmable MZI meshes, "transparent" detectors for calibration, 5 optical benches; PIXEurope pilot-line partner (2026). | PIC (SiN, SiON, InP, SiC) | https://photonics.deib.polimi.it/contacts/ (personal email on page, not reproduced) | https://photonics.deib.polimi.it/about-us/ ; https://www.deib.polimi.it/eng/deib-labs/details/85 | **5**: world-leading in 2x2 calibration and mesh tomography. |
| 13 | Electro-Optical Communication (ECO) group, Photonic Neural Networks | TU Eindhoven | NL | Patty (Ripalta) Stabile (Associate Prof.) | **2, 4**: photonic integrated matrices for optical computing (InP); TU/e also hosts JePPIX. | PIC (InP) | https://www.tue.nl/onderzoek/researchers/patty-stabile | same | **4**: photonic NN hardware with a European MPW ecosystem. |
| 14 | Neuromorphic Quantumphotonics group, Kirchhoff Institute for Physics | Heidelberg University (adjunct link to Münster) | DE | Wolfram Pernice (also KIP Executive Director) | **4**: photonic computing chips, phase-change photonics, hybrid platforms. | PIC | Generic: info@kip.uni-heidelberg.de | https://www.kip.uni-heidelberg.de/photon | **3**: top group; a 2x2 or MZI ask is below its scale. |
| 15 | Optics Laboratory (LO) and LAPD | EPFL | CH | Demetri Psaltis (LO director per EPFL news); Christophe Moser (LAPD, per EPFL news) | **1, 3**: optical neural networks with diffractive layers and multimode fibers (nPOLO, SOLO). Free-space ONN expertise. | FS / diffractive / multimode fiber | https://www.epfl.ch/labs/lo/optics-and-neural-networks | https://www.epfl.ch/labs/lo/optics-and-neural-networks ; https://www.epfl.ch/labs/lapd/optical-implementation-of-neural-networks/ | **4**: free-space ONN leaders. |
| 16 | Biomedical Photonic Imaging (wavefront shaping) | University of Twente | NL | Ivo Vellekoop | **1, 3**: SLM wavefront shaping and model-based light shaping; runs a wavefront-shaping facility open to third parties. | FS + SLM | https://www.utwente.nl/en/research/our-scientists/vellekoop/ | same | **3**: model-vs-measurement culture; biomedical focus. |

### 3c. Outside Europe (optical neural networks / programmable meshes / diffractive networks)

| # | Group / lab | Institution | Country | PI / head (public) | Ladder step: why it fits | Platform | Public contact route | Verified on (live page) | Fit |
|---|---|---|---|---|---|---|---|---|---|
| 17 | McMahon Lab | Cornell University | US | Peter McMahon (Associate Prof.) | **1-3**: physical neural networks and physics-aware training; studies the gap between a physical model and hardware, which is exactly what prospective predictions test. | FS ONN, programmable waveguides | https://mcmahon.aep.cornell.edu/contact.html | https://mcmahon.aep.cornell.edu/people.html | **4**: best conceptual match outside Europe. |
| 18 | Ozcan Research Lab | UCLA | US | Aydogan Ozcan | **3**: diffractive deep neural networks (3D-printed diffractive layers). A Neuro3D captured-scene network could be fabricated as diffractive layers. | FS diffractive (THz / visible) | https://research.seas.ucla.edu/ozcan/ (personal email on page, not reproduced) | same | **4**: diffractive-network pioneers; high demand on their time. |
| 19 | David A. B. Miller (programmable / self-configuring photonics) | Stanford University | US | David A. B. Miller (Professor Emeritus) | **2**: theory and architectures of self-configuring MZI meshes and universal linear optics. Valuable for review of the 2x2 tomography protocol. | Theory / PIC architectures | https://dabm.stanford.edu/contact/ | https://dabm.stanford.edu | **3**: advisory rather than measurement. |
| 20 | Quantum Photonics & AI Group (QPAI) | MIT | US | Dirk Englund | **2, 4**: programmable nanophotonic processors (MZI meshes) and photonic tensor cores. | PIC | https://qp.mit.edu/ (personal email on page, not reproduced) | https://qp.mit.edu/ | **3**: perfect topic; unlikely to take an unfunded small ask. |

### 3d. Facilities, MPW brokers and low-cost free-space options

| # | Facility / option | Host | Country | Head | Ladder step: why it fits | Platform | Public contact route | Verified on (live page) | Fit |
|---|---|---|---|---|---|---|---|---|---|
| 21 | Europractice: Photonics MPW | Europractice IC service | EU | n/a | **4**: MPW access to 8 foundries (imec, CEA-Leti, IHP, CORNERSTONE, AMF, GlobalFoundries, LioniX, Teem). Customers are universities, institutes and SMEs, so an academic partner is probably needed (*eligibility not verified*). | Si / SiN / glass PIC | https://europractice-ic.com/contact-us/ | https://europractice-ic.com/technologies/photonics/ | **4**: the standard MPW route once a partner exists. |
| 22 | JePPIX | Hosted at TU Eindhoven | NL | Coordinator not named on page | **4**: InP generic-integration MPW runs, PDKs, training and a pilot line. | InP PIC | Generic: coordinator@jeppix.eu ; training@jeppix.eu | https://www.jeppix.eu/ | **3**: useful later; InP is costly for steps 1-2. |
| 23 | ePIXfab | Silicon photonics alliance | EU | n/a | **4 (indirect)**: MPW activity moved to Europractice; ePIXfab now does training (Asia-Europe Si Photonics Course, Dec 2026) and community building. | Training / network | https://epixfab.eu/en/contact | https://epixfab.eu/ | **2**: for networking and training only. |
| 24 | PhotonHub Europe | EU photonics innovation hub (Horizon Europe GA 101189537) | EU | n/a | **1-4**: 8 technology platforms including **Free-Space Optics** and Si/SiN PICs; innovation support aimed at start-ups and "entrepreneurially minded researchers". | FS + PIC prototyping | https://photonhub.eu/apply-for-innovation-support/ | https://www.photonhub.eu/ | **4**: possibly the most realistic funded route; eligibility of an individual researcher needs checking. |
| 25 | openUC2 (open-source modular optics) | openUC2 GmbH, Jena (Leibniz IPHT spin-off) | DE | n/a | **1 (self-run or with a makerspace/university teaching lab)**: magnetic cube optics; a Michelson tutorial is public, and the vendor lists a Mach-Zehnder experiment in its "QBox" kit (*shop page 404 at check time; unverified*). | FS low-cost kit | Generic: hello@openuc2.com | https://openuc2.com/ ; https://hackster.io/openuc2/build-a-michelson-interferometer-in-minutes-with-openuc2-f6671b | **4**: the cheapest credible path to step 1; it still needs an independent measurer for credibility. |

### Considered but not included (verification failed or weak fit)

- **IO-CSIC (Instituto de Óptica "Daza de Valdés", Madrid)**: the group pages returned 404. The N2GO and Laser Processing groups may be relevant; re-check www.io.csic.es.
- **Exeter, C. David Wright** (phase-change photonic computing): the profile now redirects to experts.exeter.ac.uk, which returned no content. Re-verify before using.
- **Oxford, Harish Bhaskaran**: an Oxford Materials outreach page says he is on leave (serving at Apple), so not suitable now.
- **Princeton Lightwave Lab (Paul Prucnal)**: neuromorphic photonics pioneers; prucnal.princeton.edu returned 403 to the automated check.
- **iPronics (UPV spin-off)**: its homepage now centres on optical circuit switching for AI data centres, not research access to programmable processors.
- **Pavia and Münster**: no specific group was verified in this pass. Münster's photonic-computing link is covered by Pernice's adjunct role (#14).

## 4. Recommended first-contact shortlist (5)

1. **PRL-iTEAM, UPV (#1).** Spanish, nearby, and the reference group for programmable MZI meshes. A single MZI plus a 2x2 tomography is a small, well-defined task on hardware they already run. Contact via the PRL contact page, addressed to Prof. Capmany's group.
2. **TecnOPTO, UMH (#5).** A low-cost free-space MZI with an SLM phase arm suits their SLM, polarization and structured-light work, and a later step-3 SLM reproduction of a Neuro3D phase screen follows naturally. It is a Valencian-region group that can be approached in Spanish.
3. **IFISC Nonlinear Photonics / FoCo-SiNeu (#3).** A Spanish neuromorphic-photonics group with a strong culture of stability and noise measurement, which fits the visibility and phase-stability record of step 1. Use the IFISC generic address and ask for forwarding to Prof. Fischer's group.
4. **Photonic Devices Group, Politecnico di Milano (#12).** Leaders in MZI calibration and mesh programming. A short prospective-prediction comparison on an existing 2x2 cell could take little bench time.
5. **Photonics Research Group, Ghent / imec (#11).** Photonic reservoir computing plus programmable silicon photonics, and the most direct path to step 4 through imec and Europractice.

**Alternates:** GROC·UJI (#4) if TecnOPTO declines (same SLM approach); McMahon Lab (#17) for the strongest conceptual match outside Europe; PhotonHub Europe (#24) as a funded route; openUC2 (#25) as a self-built step 1 that an independent lab could then measure.

Suggested order: send 1-3 first (Spanish groups, in Spanish), wait about 2 weeks, then send 4-5 in English. Do not contact two people in the same group at once.

## 5. Outreach email template: English

> **Subject:** Small measurement collaboration: prospective predictions for a Mach-Zehnder / 2x2 optical test (Neuro3D)
>
> Dear Prof. [Surname] / Dear [Group name] team,
>
> My name is Francisco Angulo de Lafuente. I am an independent researcher based in Spain, and I develop **Neuro3D** (https://github.com/Agnuxo1/Neuro3D), an open-source coherent scalar optical neural-network simulator. Its fields and trainable phases are generated from 3D geometry (Blender), and its numerics are certified.
>
> **Stage of the project.** All results so far are simulator results; **I have no physical device yet.** As of 13 October 2026, a prospective numerical test showed that a ray/path model with free Gaussian diffraction predicts two-dimensional Mach-Zehnder interferometer output powers to within 0.004 (maximum absolute error in normalized modal power, against an independent full-wave angular-spectrum solver of the same device; not a laboratory measurement). The same work also showed limits: the captured 104-object scene falls outside the diffraction-free regime at its represented scale, and the trainable geometry spans a 12-dimensional decision family, against 26 for a free linear optical class. I would like the next step to be a physical measurement rather than more simulation.
>
> **What I am asking.** I am looking for a group willing to run a small, low-cost measurement:
> 1. a single MZI (free-space or fiber) with measured fringe visibility and phase stability, and, if that goes well,
> 2. a reconfigurable 2x2 element with transfer-matrix tomography.
>
> **How it would work.** Before any measurement, I publish the predictions and their uncertainty budget with a timestamp (a public repository release). Your group measures with your own equipment and protocol, and provides the measurement record. We then compare against the pre-registered predictions and report the result whether it agrees or not. Credit (co-authorship or acknowledgement, as you prefer) and data handling would be agreed in writing beforehand. I cannot offer funding at this stage [*optional: I can cover small consumable costs up to EUR ___*]. I estimate the bench effort at [*a few hours to one day*] once the setup exists.
>
> If this fits your interests, even as advice on the protocol, I would be glad to send a two-page measurement plan and the predictions file. Thank you for your time.
>
> Kind regards,
> Francisco Angulo de Lafuente
> Independent researcher, Spain
> https://github.com/Agnuxo1/Neuro3D
> [contact email]

## 6. Plantilla de correo: español

> **Asunto:** Colaboración de medida breve: predicciones prospectivas para un interferómetro Mach-Zehnder / red 2x2 (Neuro3D)
>
> Estimado/a Prof. [Apellido] / Estimado equipo de [grupo]:
>
> Me llamo Francisco Angulo de Lafuente. Soy investigador independiente en España y desarrollo **Neuro3D** (https://github.com/Agnuxo1/Neuro3D), un simulador abierto de redes neuronales ópticas escalares coherentes. Sus campos y fases entrenables se generan a partir de geometría 3D (Blender), y su numérica está certificada.
>
> **Estado del proyecto.** Todos los resultados hasta ahora son de simulación; **todavía no tengo ningún dispositivo físico.** A fecha de 13 de octubre de 2026, una prueba numérica prospectiva mostró que un modelo de rayos/caminos con difracción gaussiana libre predice las potencias de salida de un interferómetro Mach-Zehnder bidimensional con un error máximo de 0,004 en potencia modal normalizada, frente a un solver de ondas independiente del mismo dispositivo (no es una medida de laboratorio). Ese mismo trabajo mostró también límites: la escena capturada de 104 objetos queda fuera del régimen sin difracción a la escala representada, y la geometría entrenable abarca una familia de decisión de dimensión 12, frente a 26 de una clase óptica lineal libre. Quiero que el siguiente paso sea una medida física y no más simulación.
>
> **Qué pido.** Busco un grupo dispuesto a realizar una medida pequeña y de bajo coste:
> 1. un único MZI (espacio libre o fibra), con visibilidad de franjas y estabilidad de fase medidas, y, si sale bien,
> 2. un elemento 2x2 reconfigurable con tomografía de la matriz de transferencia.
>
> **Cómo funcionaría.** Antes de cada medida publico, con fecha, las predicciones y su presupuesto de incertidumbre (una versión en un repositorio público). Su grupo mide con su propio equipo y protocolo y aporta el registro de la medida. Después comparamos con las predicciones prerregistradas y publicamos el resultado, coincida o no. El crédito (coautoría o agradecimiento, como prefieran) y el tratamiento de los datos se acordarían por escrito antes de empezar. En esta fase no puedo ofrecer financiación [*opcional: puedo cubrir consumibles hasta ___ EUR*]. Calculo un esfuerzo de banco de [*unas horas a un día*] una vez montado el sistema.
>
> Si les interesa, aunque sea como consejo sobre el protocolo, con gusto les envío un plan de medida de dos páginas y el fichero de predicciones. Muchas gracias por su tiempo.
>
> Un cordial saludo,
> Francisco Angulo de Lafuente
> Investigador independiente, España
> https://github.com/Agnuxo1/Neuro3D
> [correo de contacto]

## 7. Notes and caveats

- **Nothing was sent.** These are drafts for Francisco to review, adapt and send himself.
- The 0.004 wording was checked against the closure report on 13 October 2026: maximum absolute error in normalized modal power against the independent angular-spectrum reference (RESULTS-WAVE-C1.md).
- Roles and leaders change. Re-check each lab page on the day of sending, especially the entries marked *uncertain*, *verify* or *partly verified*.
- Personal emails shown on some lab pages (UCM, PoliMi, UCLA, MIT, Alicante, DiOG) are deliberately left out. Use the contact page, or copy the address from the live page at sending time.
- Fit scores are this analysis's judgement of scientific and practical fit, not a forecast of replies.
