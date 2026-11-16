# Excertos literais (rate limiter em Java)

Copiados de `rfc6585.txt` e `rfc2697.txt`, baixados em 2026-11-16 de rfc-editor.org.

## F1: RFC 6585, §4 "429 Too Many Requests"

> The 429 status code indicates that the user has sent too many requests in a given amount of time ("rate limiting").

> The response representations SHOULD include details explaining the condition, and MAY include a Retry-After header indicating how long to wait before making a new request.

> Note that this specification does not define how the origin server identifies the user, nor how it counts requests.

## F2: RFC 2697, §3 "Metering"

> The maximum size of the token bucket C is CBS

> The token buckets C and E are initially (at time 0) full, i.e., the token count Tc(0) = CBS and the token count Te(0) = EBS.

> Thereafter, the token counts Tc and Te are updated CIR times per second as follows: o If Tc is less than CBS, Tc is incremented by one, else

> If Tc(t)-B >= 0, the packet is green and Tc is decremented by B down to the minimum value of 0

> the packet is red and neither Tc nor Te is decremented.

> marking of a packet with a given color requires that there be enough tokens of that color to accommodate the entire packet.

## F2: RFC 2697, §2 "Configuration"

> The srTCM is configured by setting its mode and by assigning values to three traffic parameters: a Committed Information Rate (CIR), a Committed Burst Size (CBS), and an Excess Burst Size (EBS).
