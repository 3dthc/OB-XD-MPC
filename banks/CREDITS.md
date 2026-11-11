# Factory-style patches: who made them
These patches come from the factory patch set of [OB-Xf](https://github.com/surge-synthesizer/OB-Xf) (Surge Synth Team), where every one is marked `CC0 / Public Domain` in its own file. They were converted to OB-Xd's bank format by `tools/convert_obxf_patches.py` (the inverse of OB-Xf's own OB-Xd importer), with two changes for the MPC: the voice count stops at 10 (5 with unison) so the CPU keeps up, and each patch's Volume is set so they play at a similar level without clipping (`tools/make_cc0_levels.py`). CC0 asks for no credit; it is given here anyway.

Banks 010-012 are exact conversions. Banks 013-015 (the ones ending in "2") use OB-Xf features OB-Xd does not have (xpander filter, ring mod, noise colour, second LFO, inverted envelopes); those parts are dropped or mapped to the nearest OB-Xd equivalent (xpander becomes the 4-pole low pass), so these patches are close to the originals but not identical.

## Keys (27 patches)

| Patch | Author | Category |
|---|---|---|
| Acoustic Piano 3 | Aleksey Zhehanov | Keys |
| An Ocean Swift | Ocean Swift | Keys |
| CP Seventy | Aleksey Zhehanov | Keys |
| E. Piano 2 | John Valentine | Keys |
| Everything | Vincent Zauhar | Keys |
| Harpkies | Saif Sameer | Keys |
| Harpsi | John Valentine | Keys |
| Harpsichord | 0.5° | Keys |
| It's an OB-X! | Saif Sameer | Keys |
| J60 Neon Main | Saif Sameer | Keys |
| J60 Neon PW 1 | Saif Sameer | Keys |
| MelloWow | Saif Sameer | Keys |
| OB Piano | Saif Sameer | Keys |
| OBX Clavinet | Saif Sameer | Keys |
| Smoothful | Saif Sameer | Keys |
| Subtle | Saif Sameer | Keys |
| Sweet Spot | Vincent Zauhar | Keys |
| Twindlin' | Saif Sameer | Keys |
| J60 PWM Pluck | Saif Sameer | Plucks |
| J60 Saw Pluck | Saif Sameer | Plucks |
| Pizzi | Saif Sameer | Plucks |
| Simple Saw Pluck | Saif Sameer | Plucks |
| Glockenspiel | Aleksey Zhehanov | Mallets |
| Tubular Bells | Aleksey Zhehanov | Mallets |
| Xylophone | Aleksey Zhehanov | Mallets |
| Clicky Nostalgia | Vincent Zauhar | Bells |
| Steel String Guitar 2 | Aleksey Zhehanov | Guitars |

## Bass+Lead (19 patches)

| Patch | Author | Category |
|---|---|---|
| '32 Rez Bass | Vincent Zauhar | Basses |
| Diver | Saif Sameer | Basses |
| Electric Bass 1 | Saif Sameer | Basses |
| Muffler | Saif Sameer | Basses |
| OBX Bass 1 | Saif Sameer | Basses |
| OBX Bass 2 | Saif Sameer | Basses |
| Slim Jim | Saif Sameer | Basses |
| Veberly Hills | Saif Sameer | Basses |
| Xmodec | Saif Sameer | Basses |
| Dimmerton | Saif Sameer | Leads |
| Halogenic | Saif Sameer | Leads |
| Heverly Bills | Saif Sameer | Leads |
| Mono Monsta | Ocean Swift | Leads |
| Recorders | Saif Sameer | Leads |
| Rock Unison | Saif Sameer | Leads |
| Saucer | Saif Sameer | Leads |
| Street Hawk | Saif Sameer | Leads |
| Super-Saw | Vincent Zauhar | Leads |
| Unison Fear | Saif Sameer | Leads |

## Pads+FX (33 patches)

| Patch | Author | Category |
|---|---|---|
| Tremolo | Black Sided Sun | Pads |
| Warmth | Saif Sameer | Pads |
| Fast Strings | Saif Sameer | Strings |
| Low Strings | Saif Sameer | Strings |
| Soft Strings | Saif Sameer | Strings |
| Swept Tremolo Strings | Black Sided Sun | Strings |
| J106 Brass | Saif Sameer | Brass |
| J60 Brass | Saif Sameer | Brass |
| J60 Sub PWM | Saif Sameer | Brass |
| Might As Well... | EvilDragon | Brass |
| Pursuit Mono | Saif Sameer | Brass |
| Triumpher | Saif Sameer | Brass |
| Truimpher | Saif Sameer | Brass |
| Vuvuzela Jam | 0.5° | Winds |
| Hold One Back | Ocean Swift | Soundscapes |
| Saucer | Saif Sameer | Soundscapes |
| Bubbler | 0.5° | FX |
| Downer Regular | Saif Sameer | FX |
| Downer Resonant | Saif Sameer | FX |
| Downer Swoosh | Saif Sameer | FX |
| Electrons | Saif Sameer | FX |
| Metal Cross | Ocean Swift | FX |
| OBX Jet | Saif Sameer | FX |
| Psy Pow 1 | Ocean Swift | FX |
| Psy Pow 2 | Ocean Swift | FX |
| Uplift Regular | Saif Sameer | FX |
| Uplift Resonant | Saif Sameer | FX |
| Uplift Swoosh | Saif Sameer | FX |
| Conga | Aleksey Zhehanov | Percussion |
| Conga Muted | Aleksey Zhehanov | Percussion |
| Shaker | Aleksey Zhehanov | Percussion |
| Kick 1 | Aleksey Zhehanov | Drums |
| Kick 4 | Aleksey Zhehanov | Drums |

## Keys 2 (119 patches)

| Patch | Author | Category |
|---|---|---|
| Accordion 1 | John Valentine | Keys |
| Accordion 1 | Aleksey Zhehanov | Keys |
| Accordion 2 | Aleksey Zhehanov | Keys |
| Accordion 3 | Aleksey Zhehanov | Keys |
| Accordion 4 | Aleksey Zhehanov | Keys |
| Accordion 5 | Aleksey Zhehanov | Keys |
| Acoustic Piano 1 | Aleksey Zhehanov | Keys |
| Acoustic Piano 2 | Aleksey Zhehanov | Keys |
| Almondo | Saif Sameer | Keys |
| An Ocean Song | Ocean Swift | Keys |
| Anastasia | Ocean Swift | Keys |
| Arpsichord | Jacky Ligon | Keys |
| Blown Bottle | Black Sided Sun | Keys |
| Brokeneon | Saif Sameer | Keys |
| Clavinet | Aleksey Zhehanov | Keys |
| E. Piano 1 | John Valentine | Keys |
| E. Piano 3 | Aleksey Zhehanov | Keys |
| E. Piano 4 | Aleksey Zhehanov | Keys |
| E. Piano 4 Chorus | Aleksey Zhehanov | Keys |
| E. Piano 4 Tremolo | Aleksey Zhehanov | Keys |
| Early Piano | Fedir Tkachov | Keys |
| Elarisin | Saif Sameer | Keys |
| Electric Piano 3 | Aleksey Zhehanov | Keys |
| Elegant EP | Saif Sameer | Keys |
| Evolution Arp | Pebblestream | Keys |
| Formant Reeds | Jacky Ligon | Keys |
| Galactikey | Saif Sameer | Keys |
| Good Ending | Fedir Tkachov | Keys |
| Gritty | 0.5° | Keys |
| Guitary | Fedir Tkachov | Keys |
| Harmonica | Aleksey Zhehanov | Keys |
| Honky Tonk | Aleksey Zhehanov | Keys |
| Icy Kalimba | Pebblestream | Keys |
| Interstellar Dark | Black Sided Sun | Keys |
| J60 Neon PW 2 | Saif Sameer | Keys |
| JX E. Piano 1 | Saif Sameer | Keys |
| JX E. Piano 2 | Saif Sameer | Keys |
| JX E. Piano 3 | Saif Sameer | Keys |
| Kawari | Saif Sameer | Keys |
| Leakeys | Saif Sameer | Keys |
| Lighthearted | Fedir Tkachov | Keys |
| Lo-Fi Piano | 0.5° | Keys |
| Moon Piano 1 | Black Sided Sun | Keys |
| Moon Piano 2 | Black Sided Sun | Keys |
| Moon Piano 3 | Black Sided Sun | Keys |
| Mouth Keys | Ocean Swift | Keys |
| No Fate | Artur Rembe | Keys |
| No Longer Do I Tread The Sand Barefoot | Artur Rembe | Keys |
| Noireon | Saif Sameer | Keys |
| Obiekies | Saif Sameer | Keys |
| PleasanTri | Jacky Ligon | Keys |
| Polee Quaire | Black Sided Sun | Keys |
| Porta-Keys | Jacky Ligon | Keys |
| Pulled PWM | Saif Sameer | Keys |
| Reed Organ | Jacky Ligon | Keys |
| Return Youngman | Saif Sameer | Keys |
| Rondo | Fedir Tkachov | Keys |
| Santori Time | Fedir Tkachov | Keys |
| SEM Piano | Saif Sameer | Keys |
| Separate Journey | Saif Sameer | Keys |
| Siner | Artur Rembe | Keys |
| Space Bells | Saif Sameer | Keys |
| Spacekies | Saif Sameer | Keys |
| Subtler | Saif Sameer | Keys |
| The Cold Seventh | Artur Rembe | Keys |
| Thin Plinky | Black Sided Sun | Keys |
| Zen Garden | Fedir Tkachov | Keys |
| Acidisillification | 0.5° | Plucks |
| Bright Side | Fedir Tkachov | Plucks |
| Firefly Embers | 0.5° | Plucks |
| On Bent Key | Ocean Swift | Plucks |
| Pacer | Saif Sameer | Plucks |
| Riff Structure | Saif Sameer | Plucks |
| Small Steps | Fedir Tkachov | Plucks |
| Voyet Sqrx | Saif Sameer | Plucks |
| Mallet Release | Black Sided Sun | Mallets |
| Mallet Synth | Black Sided Sun | Mallets |
| Marimba | Aleksey Zhehanov | Mallets |
| Simple Mallet | Black Sided Sun | Mallets |
| Steel Drums | Aleksey Zhehanov | Mallets |
| Vibraphone | Aleksey Zhehanov | Mallets |
| Inharm Bella | Ocean Swift | Bells |
| Stabbed Hand Pan | 0.5° | Bells |
| Banjo | Aleksey Zhehanov | Guitars |
| Clean Guitar | Aleksey Zhehanov | Guitars |
| Clean Guitar Chorus | Aleksey Zhehanov | Guitars |
| Clean Guitar Muted | Aleksey Zhehanov | Guitars |
| Distorted Guitar 1 | Aleksey Zhehanov | Guitars |
| Distorted Guitar 2 | Aleksey Zhehanov | Guitars |
| Distorted Guitar Muted | Aleksey Zhehanov | Guitars |
| Flageolet | Aleksey Zhehanov | Guitars |
| Fret Noise | Aleksey Zhehanov | Guitars |
| Funk Guitar | Aleksey Zhehanov | Guitars |
| Jazz Guitar | Aleksey Zhehanov | Guitars |
| Nylon String Guitar | Aleksey Zhehanov | Guitars |
| Overdrive Guitar | Aleksey Zhehanov | Guitars |
| Power Chord | Aleksey Zhehanov | Guitars |
| Power Chord 2 | Aleksey Zhehanov | Guitars |
| Power Chord Muted | Aleksey Zhehanov | Guitars |
| Power Chord Muted 2 | Aleksey Zhehanov | Guitars |
| Steel String Guitar | Aleksey Zhehanov | Guitars |
| Steel String Guitar DT | Aleksey Zhehanov | Guitars |
| Carborgen | Saif Sameer | Organs |
| Church Organ | Aleksey Zhehanov | Organs |
| Continental | Aleksey Zhehanov | Organs |
| Haunted Reeds | 0.5° | Organs |
| Klassika | Saif Sameer | Organs |
| Laurens Organ | Aleksey Zhehanov | Organs |
| Oberphisa | Saif Sameer | Organs |
| Old Timer | Black Sided Sun | Organs |
| Organ Flutes | Black Sided Sun | Organs |
| Percussive Organ 1 | Aleksey Zhehanov | Organs |
| Percussive Organ 2 | Aleksey Zhehanov | Organs |
| Rocker | Saif Sameer | Organs |
| Rotary Organ 2 | Aleksey Zhehanov | Organs |
| Rotary Organ 2 | Aleksey Zhehanov | Organs |
| Tonewheels | Vincent Zauhar | Organs |
| Transistorg | Saif Sameer | Organs |
| Wrong Organ | Ocean Swift | Organs |

## Bass+Lead 2 (64 patches)

| Patch | Author | Category |
|---|---|---|
| Acoustic Bass | Aleksey Zhehanov | Basses |
| Back To The Future | Artur Rembe | Basses |
| Blastine | Saif Sameer | Basses |
| Definitely Below | Artur Rembe | Basses |
| Didger Saw | Ocean Swift | Basses |
| Dubber Bass | Ocean Swift | Basses |
| Electric Bass 2 | Aleksey Zhehanov | Basses |
| Electric Bass 3 | Aleksey Zhehanov | Basses |
| Electric Bass 3 Muted | Aleksey Zhehanov | Basses |
| Expanded | Jacky Ligon | Basses |
| Faxi Slap | Ocean Swift | Basses |
| Fretless Bass | Aleksey Zhehanov | Basses |
| Hit It | Vincent Zauhar | Basses |
| Ignitor | Saif Sameer | Basses |
| Meltomedia | Saif Sameer | Basses |
| Nadir | Black Sided Sun | Basses |
| Ninja Turtle | Ocean Swift | Basses |
| Notchsense | Jacky Ligon | Basses |
| Outer Bass | Jacky Ligon | Basses |
| Picked Bass | Aleksey Zhehanov | Basses |
| Possible Funk | Jacky Ligon | Basses |
| Rapider | Saif Sameer | Basses |
| Retrowaver | Saif Sameer | Basses |
| Rolling Bass | John Valentine | Basses |
| Running Bass | Pebblestream | Basses |
| Sawdust | Vincent Zauhar | Basses |
| Slap Bass | Aleksey Zhehanov | Basses |
| Stealth Bass | Pebblestream | Basses |
| Thick Unison | Pebblestream | Basses |
| Uni Frog | Ocean Swift | Basses |
| Velux | Saif Sameer | Basses |
| Watery Filter | Vincent Zauhar | Basses |
| Whoa Bace | Pebblestream | Basses |
| Xmod Stack | Saif Sameer | Basses |
| 2077 Lead | Black Sided Sun | Leads |
| 8VM Lead | EvilDragon | Leads |
| Abyss Lead | Black Sided Sun | Leads |
| Drunk Glider | 0.5° | Leads |
| Five Double | Black Sided Sun | Leads |
| Five Eight Toy | Black Sided Sun | Leads |
| Formant Lead | Jacky Ligon | Leads |
| Funk Lead | Jacky Ligon | Leads |
| FunKey | Jacky Ligon | Leads |
| Funky Cat | 0.5° | Leads |
| Funky Munky | Pebblestream | Leads |
| Gasp Lead | Black Sided Sun | Leads |
| Mean Lead | Black Sided Sun | Leads |
| Miwara | Saif Sameer | Leads |
| Monoplane Glide | Ocean Swift | Leads |
| Muuger | Artur Rembe | Leads |
| Plasticon | Saif Sameer | Leads |
| Pulsapart | Saif Sameer | Leads |
| Pulsrage | Saif Sameer | Leads |
| Resweeper | Saif Sameer | Leads |
| Scanners | Black Sided Sun | Leads |
| Shadow Sync | Saif Sameer | Leads |
| SIDicious | Black Sided Sun | Leads |
| Smother Lead | Black Sided Sun | Leads |
| Strained Filtah | Black Sided Sun | Leads |
| Thruster | Saif Sameer | Leads |
| Tri-Things | Jacky Ligon | Leads |
| Tungsten Sync | Saif Sameer | Leads |
| Unison SIDicious | Black Sided Sun | Leads |
| Xcentor | Saif Sameer | Leads |

## Pads+FX 2 (128 patches)

| Patch | Author | Category |
|---|---|---|
| 5 AM Pad | Artur Rembe | Pads |
| Astheas | Jacky Ligon | Pads |
| Aziteta | Jacky Ligon | Pads |
| Breathe | Fedir Tkachov | Pads |
| Canada | 0.5° | Pads |
| Carbonized | Black Sided Sun | Pads |
| Childhood | Black Sided Sun | Pads |
| Cry In The Sky | Ocean Swift | Pads |
| Cythrata | Saif Sameer | Pads |
| Dark Future | Black Sided Sun | Pads |
| Dhyana | Black Sided Sun | Pads |
| Die Alone | Artur Rembe | Pads |
| Discovery | 0.5° | Pads |
| Dramady More | Ocean Swift | Pads |
| Dreaming Anew | Jacky Ligon | Pads |
| Emoshi | Saif Sameer | Pads |
| Ephur | Jacky Ligon | Pads |
| Eternal Departure | Black Sided Sun | Pads |
| Fading Memory | Den Rize | Pads |
| Fissures | Jacky Ligon | Pads |
| Fizzy | John Valentine | Pads |
| Flowcasionally | Jacky Ligon | Pads |
| Give It Time | Fedir Tkachov | Pads |
| Glitchorin | Saif Sameer | Pads |
| In Sweep | Black Sided Sun | Pads |
| It's Complicated | Fedir Tkachov | Pads |
| Just A Pad | Black Sided Sun | Pads |
| Minor 6 | Pebblestream | Pads |
| Minthus | Jacky Ligon | Pads |
| Mission To Mars | Artur Rembe | Pads |
| Morning Glow | Artur Rembe | Pads |
| My Maya | Ocean Swift | Pads |
| Nanotube | Jacky Ligon | Pads |
| New Day | Fedir Tkachov | Pads |
| OB One | Black Sided Sun | Pads |
| OBelisk | Jacky Ligon | Pads |
| Ocean Pits | Ocean Swift | Pads |
| Optyd | Jacky Ligon | Pads |
| Other Dream | Jacky Ligon | Pads |
| Othirs | Jacky Ligon | Pads |
| Ounor | Jacky Ligon | Pads |
| Quozosm | Jacky Ligon | Pads |
| Remembrance | Black Sided Sun | Pads |
| Rich | Den Rize | Pads |
| Ripley | Saif Sameer | Pads |
| Sadness Radio | Den Rize | Pads |
| Seocang | Jacky Ligon | Pads |
| Settling | Vincent Zauhar | Pads |
| Soriniscape | Jacky Ligon | Pads |
| Sun Ray | Pebblestream | Pads |
| Super Drama | Ocean Swift | Pads |
| Sweeprise | Black Sided Sun | Pads |
| Tremolo Choir | 0.5° | Pads |
| Unfolding | Black Sided Sun | Pads |
| Usthavur | Jacky Ligon | Pads |
| Vintage Swell | Saif Sameer | Pads |
| Violord | Jacky Ligon | Pads |
| Walking On Shells | John Valentine | Pads |
| Wasteland One | Black Sided Sun | Pads |
| Wasteland Two | Black Sided Sun | Pads |
| Waveling | Saif Sameer | Pads |
| Xatal | Jacky Ligon | Pads |
| Attack Strings | Saif Sameer | Strings |
| Cello | Aleksey Zhehanov | Strings |
| Double Bass | Aleksey Zhehanov | Strings |
| Gentle Synthy Ensemble | 0.5° | Strings |
| Harmonic Sweep Strings | 0.5° | Strings |
| Harp | Aleksey Zhehanov | Strings |
| High Strings | Saif Sameer | Strings |
| Marcato Strings | Aleksey Zhehanov | Strings |
| Pizzicato Strings | Aleksey Zhehanov | Strings |
| Sombre Dance | Fedir Tkachov | Strings |
| String Machine | Black Sided Sun | Strings |
| String Section Large | Aleksey Zhehanov | Strings |
| String Section Small | Aleksey Zhehanov | Strings |
| Stringesque | Vincent Zauhar | Strings |
| Tremolo Strings | Aleksey Zhehanov | Strings |
| Uneasy Strings | 0.5° | Strings |
| Unison Strings | Aleksey Zhehanov | Strings |
| Viola | Aleksey Zhehanov | Strings |
| Violin | Aleksey Zhehanov | Strings |
| Accented | Saif Sameer | Brass |
| Brass Section Chords | 0.5° | Brass |
| Brass Stabs | Vincent Zauhar | Brass |
| Bright Mono Brass | Saif Sameer | Brass |
| Bright Trombone | Aleksey Zhehanov | Brass |
| Euphonium | Aleksey Zhehanov | Brass |
| Euphonium Ensemble | Aleksey Zhehanov | Brass |
| French Horn | Aleksey Zhehanov | Brass |
| French Horn Ensemble | Aleksey Zhehanov | Brass |
| Horn Section | Saif Sameer | Brass |
| Obright Original | Saif Sameer | Brass |
| Obright Stereo | Saif Sameer | Brass |
| Prophet | Saif Sameer | Brass |
| ProphOBe | Saif Sameer | Brass |
| Pursuit Bright | Saif Sameer | Brass |
| Reed Horns | Saif Sameer | Brass |
| Silky Polybrass | Saif Sameer | Brass |
| Trombone | Aleksey Zhehanov | Brass |
| Trombone Ensemble | Aleksey Zhehanov | Brass |
| Trumpet | Aleksey Zhehanov | Brass |
| Trumpet Ensemble | Aleksey Zhehanov | Brass |
| Trumpet Muted | Aleksey Zhehanov | Brass |
| Trumpet Soft | Aleksey Zhehanov | Brass |
| Tuba | Aleksey Zhehanov | Brass |
| Alto Sax | Aleksey Zhehanov | Winds |
| Alto Sax Ensemble | Aleksey Zhehanov | Winds |
| Alto Sax Growl | Aleksey Zhehanov | Winds |
| Baritone Sax | Aleksey Zhehanov | Winds |
| Bassoon | Aleksey Zhehanov | Winds |
| Clarinet | Aleksey Zhehanov | Winds |
| Clarinet Ensemble | Aleksey Zhehanov | Winds |
| English Horn | Aleksey Zhehanov | Winds |
| Flute | John Valentine | Winds |
| Oboe | Aleksey Zhehanov | Winds |
| Piccolo | Aleksey Zhehanov | Winds |
| Reeder | Saif Sameer | Winds |
| Soprano Sax | Aleksey Zhehanov | Winds |
| Tenor Sax | Aleksey Zhehanov | Winds |
| Tenor Sax Ensemble | Aleksey Zhehanov | Winds |
| Tenor Sax Soft | Aleksey Zhehanov | Winds |
| Clicky | Fedir Tkachov | Soundscapes |
| Dark Wave | Black Sided Sun | Soundscapes |
| Green Fury | Black Sided Sun | Soundscapes |
| In The Sky | Black Sided Sun | Soundscapes |
| Incenses | Black Sided Sun | Soundscapes |
| Into Cinemas | Ocean Swift | Soundscapes |
| It Is Alive | Black Sided Sun | Soundscapes |
