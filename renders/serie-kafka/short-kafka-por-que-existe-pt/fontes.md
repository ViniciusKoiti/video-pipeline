# Fontes — Por que o Kafka existe? (short-kafka-por-que-existe-pt)

Textos baixados em 2026-11-15, numerados em `../fontes/`. App, serviços e pedidos são fictícios (cenário didático).
Sem medição: nenhum número nosso na fala nem na tela.

| Cena | Fala ou tela | Fonte | Trecho literal |
| --- | --- | --- | --- |
| `abertura`, `direto`, `cliente` | app de delivery, serviço de pedidos que chama um por vez, notificações no celular | cenário didático | — |
| `topico` | "ele escreve o evento uma vez num tópico e segue. Cada serviço lê no seu ritmo." | K-INT P31 | "producers and consumers are fully decoupled and agnostic of each other [...] For example, producers never need to wait for consumers." |
| `topico` | tópico com vários consumidores | K-INT P32 | "Topics in Kafka are always multi-producer and multi-subscriber: a topic can have zero, one, or many producers that write events to it, as well as zero, one, or many consumers that subscribe to these events." |
| `codigo` | `producer.send(...)`, "o serviço segue sem esperar ninguém" | K-INT P31; K-DES P54 (Asynchronous send) | "producers never need to wait for consumers." |
| `falha` | "o evento fica guardado no tópico" | K-INT P32 | "Events in a topic can be read as often as needed-unlike traditional messaging systems, events are not deleted after consumption. Instead, you define for how long Kafka should retain your events through a per-topic configuration setting" |
| `falha` | "e ele lê quando voltar" | K-DES P68 | "the position of a consumer in each partition is just a single integer, the offset of the next message to consume." |
| `decisao` | "O custo é um cluster para operar, ou um serviço gerenciado." | K-INT P24; K-INT P21 | "Kafka is run as a cluster of one or more servers" / "You can choose between self-managing your Kafka environments and using fully managed services offered by a variety of vendors." |
| `decisao` | "O ganho é desacoplar." | K-INT P31 | "producers and consumers are fully decoupled and agnostic of each other, which is a key design element to achieve the high scalability that Kafka is known for." |

Motivação dos autores (contexto da série, não dita neste corte): K-DES P5, "We designed Kafka to be able to act as
a unified platform for handling all the real-time data feeds a large company might have."

Leitura editorial (sem fonte direta): chamar "custo" a operação do cluster é uma avaliação do roteiro, apoiada em
K-INT P21 e P24.
