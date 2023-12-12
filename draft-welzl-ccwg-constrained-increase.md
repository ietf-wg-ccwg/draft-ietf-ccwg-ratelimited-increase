---
title: "Constrained Increase of the Congestion Window"
category: std

docname: draft-welzl-ccwg-constrained-increase-latest
submissiontype: IETF  # also: "independent", "editorial", "IAB", or "IRTF"
number:
date:
consensus: true
v: 3
area: "Transport"
workgroup: "Congestion Control Working Group"
keyword:
 - next generation
 - unicorn
 - sparkling distributed ledger
venue:
  group: "Congestion Control Working Group"
  type: "Working Group"
  mail: "ccwg@ietf.org"
  arch: "https://mailarchive.ietf.org/arch/browse/ccwg/"
  github: "mwelzl/draft-ccwg-constrained-increase"
  latest: "https://mwelzl.github.io/draft-ccwg-constrained-increase/draft-welzl-ccwg-constrained-increase.html"

author:
 -
    ins: M. Welzl
    name: Michael Welzl
    org: University of Oslo
    street: PO Box 1080 Blindern
    city: 0316  Oslo
    country: Norway
    email: michawe@ifi.uio.no
    uri: http://welzl.at/
  -
    ins: T. Henderson
    name: Tom Henderson
    org: Please fill out your affiliation
    street: and street etc., though...
    street: it's really optional, I think.
    city: City
    country: Country
    email: tomh@tomh.org
    uri: https://tomh.org/
  -
    ins: G. Fairhurst
    name: Godred Fairhurst
    org: University of Aberdeen
    street: Department of Engineering
    street: Fraser Noble Building
    city: Aberdeen, AB24 3UE
    country: Scotland
    email: gorry@erg.abdn.ac.uk
    uri: https://www.erg.abdn.ac.uk/
  -

normative:

informative:


--- abstract

This document specifies how transport protocols should increase their congestion window when the sender is constrained, either by the application stopping to supply data or by flow control.


--- middle

# Introduction

TODO Introduction and now I'm really still only testing this.


# Material

* ns-3: *

This whole thing started with ns-3 taking the spec word by word, and letting cwnd grow endlessly in response to ACKs even when rwnd or the sending application limit the sender. I claimed that “real implementations don’t do that”.


* Linux: *

Tom was able to confirm that, indeed, Linux TCP will *not* increase cwnd upon incoming ACKs when any such limit applies. He found this by testing it, and we can also see it in the code:
https://lxr.linux.no/linux+v6.0.9/net/ipv4/tcp_cong.c#L450
Here’s the increase function, with this check:
        if (!tcp_is_cwnd_limited(sk))
                return;

“tcp_is_cwnd_limited" is a function in tcp.h which checks the flag: "tp->is_cwnd_limited”, and I tried to find where this flag is set. I found:
https://lxr.linux.no/linux+v6.0.9/net/ipv4/tcp_output.c#L2612
where it is initialised to false, followed by:
https://lxr.linux.no/linux+v6.0.9/net/ipv4/tcp_output.c#L2717
"is_cwnd_limited |= (tcp_packets_in_flight(tp) >= tcp_snd_cwnd(tp));”

So whenever (and, because of the initialisation, only when!) the sender is greedy (the more common case of “=“ rather than “>”), this will set “is_cwnd_limited” to true. Tom confirmed the behaviour, both for Reno and Cubic.


* Others: *

We haven’t checked. We could look at FreeBSD code, and do tests with Windows, or Apple… or we could just ask people.



Other RFCs:
- - - - - - - - - - -

There's an interesting mix of things!


* Cubic: *

RFC 9438 says: Cubic doesn't increase cwnd when it's limited by the sending application or rwnd. See: https://www.rfc-editor.org/rfc/rfc9438.html#name-behavior-for-application-li
The older RFC (RFC 8312) didn’t include rwnd in this text, but it seems they decided to fix this now: https://www.rfc-editor.org/rfc/rfc8312.html#section-5.8 


* SCTP: *

https://www.rfc-editor.org/rfc/rfc9260.html#name-slow-start says: "When cwnd is less than or equal to ssthresh, an SCTP endpoint MUST use the slow-start algorithm to increase cwnd only if the current congestion window is being fully utilized and the data sender is not in Fast Recovery. Only when these two conditions are met can the cwnd be increased; otherwise, the cwnd MUST NOT be increased.”

This is very good, in my opinion, BUT it’s a bit awkward that this text appears only in the “slow start” section, and the "congestion avoidance” section doesn’t even point back at this.


* QUIC: *

To me, QUIC has the best phrasing of the issue:
https://www.rfc-editor.org/rfc/rfc9002.html#name-underutilizing-the-congesti
"When bytes in flight is smaller than the congestion window and sending is not pacing limited, the congestion window is underutilized. This can happen due to insufficient application data or flow control limits. When this occurs, the congestion window SHOULD NOT be increased in either slow start or congestion avoidance.

A sender that paces packets (see Section 7.7) might delay sending packets and not fully utilize the congestion window due to this delay. A sender SHOULD NOT consider itself application limited if it would have fully utilized the congestion window without pacing delay."

Interesting, isn’t it: this is the first one to mention pacing. So this would be the case of the application itself implementing pacing, not the stack. I agree with the statement about it - but I’m unsure about the first SHOULD NOT: to me, a MUST NOT with the exception of the pacing would have been better.


# Conventions and Definitions

{::boilerplate bcp14-tagged}


# Security Considerations

TODO Security


# IANA Considerations

This document has no IANA actions.


--- back

# Acknowledgments
{:numbered="false"}

TODO acknowledge.
