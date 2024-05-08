---
title: "Increase of the Congestion Window when the Sender Is Rate-Limited"
abbrev: "Constrained cwnd Increase"
category: std

docname: draft-welzl-ccwg-ratelimited-increase-latest
submissiontype: IETF  # also: "independent", "editorial", "IAB", or "IRTF"
number:
date:
updates: RFC5681, RFC9002, RFC9260, RFC9438
consensus: true
v: 3
area: "Transport"
workgroup: "Congestion Control Working Group"
venue:
  group: "Congestion Control Working Group"
  type: "Working Group"
  mail: "ccwg@ietf.org"
  arch: "https://mailarchive.ietf.org/arch/browse/ccwg/"
  github: "mwelzl/draft-ccwg-constrained-increase"
  latest: "https://mwelzl.github.io/draft-ccwg-constrained-increase/draft-welzl-ccwg-constrained-increase.html"

stand_alone: yes
smart_quotes: no
pi: [toc, sortrefs, symrefs]

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
    city: Mercer Island, WA
    country: United States
    email: tomh@tomh.org
    uri: https://www.tomh.org/
  -
    ins: G. Fairhurst
    name: Godred Fairhurst
    org: University of Aberdeen
    street: School of Engineering
    street: Fraser Noble Building
    city: Aberdeen, AB24 3UE
    country: UK
    email: gorry@erg.abdn.ac.uk
    uri: https://www.erg.abdn.ac.uk/

normative:

informative:
I-D.cardwell-iccrg-bbr-congestion-control:


--- abstract

This document specifies how transport protocols increase their congestion window when the sender is rate-limited.
Such a limitation can be caused by the sending application not supplying data or by receiver flow control.


--- middle

# Introduction

A sender of a congestion controlled transport protocol becomes "rate-limited" when it does not send any data
even though the congestion control rules would allow it to transmit data.
This could occur because the application has not provided sufficient data to fully utilise the congestion window (cwnd).
It could also occur because the receiver has limited the sender using flow control
(e.g., by the advertised TCP receiver window (rwnd) or by the conection or stream flow credit in quic).
Current RFCs specifying congestion control mechanisms diverge regarding the rules for increasing the cwnd when the sender is rate-limited.

Congestion Window Validation (CWV) {{?RFC7661}} provides an experimental specification defining how to manage a cwnd that has
become larger than the current flight size.
In contrast, this present document concerns the increase in cwnd when a sender is rate-limited. These two topics are distinct,
but are related, because both describe the management of the cwnd when the sender does not fully utilise the current cwnd.

This document specifies a uniform rule that congestion control mechanisms MUST apply and provides a recommendation that congestion control implementations SHOULD follow.
An appendix provides an overview of the divergence in current RFCs and some current implementations regarding cwnd increase when the sender is rate-limited.

## Terminology

This document uses the terms defined in {{Section 2 of !RFC5681}}.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Increase rules {#rules}

Irrespective of the current state of a congestion control mechanism, senders using a congestion controlled transport protocol:

1. MUST include a limit to the growth of cwnd when FlightSize < cwnd.
2. SHOULD limit the growth of cwnd when FlightSize < cwnd with inc(maxFS).

In rule #2, "inc" is a function that returns the maximum unconstrained increase that would result from the congestion control mechanism within one RTT, based on the "maxFS" parameter.
For example, for Slow Start, as specified in {{!RFC5681}}, inc(maxFS)=2*maxFS, such that equation 2 in {{!RFC5681}} becomes:

~~~
cwnd_new = cwnd + min (N, SMSS)
cwnd = min(cwnd_new, 2*maxFS)
~~~

Similarly, with rule #2 applied to Congestion Avoidance, inc(maxFS)=1+maxFS, such that equation 3 in {{!RFC5681}} becomes:

~~~
cwnd_new = cwnd + SMSS*SMSS/cwnd
cwnd = min(cwnd_new, 1+maxFS)
~~~

maxFS is the largest value of FlightSize since the last time that cwnd was decreased.
If cwnd has never been decreased, maxFS is the maximum value of FlightSize since the start of the data transfer.

## Discussion

If the sending rate is less than permitted by cwnd for multiple RTTs, limited either by the sending application or by the receiver-advertised window, continuously increasing the cwnd would cause a mismatch between the cwnd and the capacity that the path supports (i.e., over-estimating the capacity).
Such unlimited growth in the cwnd is therefore disallowed by the first rule.

However, in most common congestion control mechanisms, in the absence of an indication of congestion, a cwnd that has been fully utilized during an RTT is permitted to be increased during the immediately following RTT.
Thus, such an increase is allowed by the second rule.


### Rate-based congestion control

The present document updates congestion control specifications that use a congestion window (cwnd) to limit the number of unacknowledged packets a sender is allowed to emit. Use of a congestion window variable to control sending rate is not the only mechanism available and used in practice.

Congestion control mechanisms can also constrain data transmission by explicitly calculating the sending rate over some time interval, by "pacing" packets (injecting pauses in between their transmission) or via combinations of the above (e.g., BBR combines these three methods {{?I-D.cardwell-iccrg-bbr-congestion-control}}). The guiding principle behind the rules in {{rules}} applies to all  congestion control mechanisms: in the absence of a congestion indication, a sender should be allowed to increase its rate from the amount of data that it has transmitted during the previous RTT. This holds irrespective of whether the sender is rate-limited or not.


### Pacing

Pacing mechanisms seek to avoid the negative impacts associated with "bursts" (flights of packets transmitted back-to-back). This is usually without limiting the number of packets that are sent per RTT. The present specification introduces a limitation using "maxFS", which is measured over an RTT; thus, as long as the number of packets per RTT is unaffected by pacing, the rules in {{rules}} also do not constrain the use of pacing mechanisms.


# Security Considerations

While congestion control designs could result in unwanted competing traffic, they do not directly result in new security considerations.

Transport protocols that provide authentication (including those using encryption), or are carried over protocols that provide authentication,
can protect their congestion control mechanisms from network attack. This is orthogonal to the congestion control rules.

# IANA Considerations

This document requests no IANA action.


--- back

<!-- # Acknowledgments
{:numbered="false"}

TODO acknowledge. Note, numbered sections shouldn't appear
after an unnumbered one - so either move this last, or take
the numbering rule out. -->


# The state of RFCs and implementations

This section is provided as input for IETF discussion, and should be removed before publication.

## TCP ("Reno" congestion control)

### Specification

{{!RFC5681}} does not contain a rule to limit the growth of cwnd when the sender is rate-limited. This statement (page 8) gives an impression that such cwnd growth might be expected:

>Implementation Note: An easy mistake to make is to simply use cwnd, rather than FlightSize, which in some implementations may incidentally increase well beyond rwnd.

{{?RFC7661}} also suggests there is no increase limitation in the standard TCP behavior (which {{?RFC7661}} changes), on page 4:

>Standard TCP does not impose additional restrictions on the growth of
the congestion window when a TCP sender is unable to send at the
maximum rate allowed by the cwnd. In this case, the rate-limited
sender may grow a cwnd far beyond that corresponding to the current
transmit rate, resulting in a value that does not reflect current
information about the state of the network path the flow is using.

### Implementation {#tcp-impl}

- ns-2 allows cwnd to grow when it is rate-limited by rwnd. (Rate-limited by the sending application: not tested.)
- ns-3 allows cwnd to grow when it is rate-limited by either an application or the rwnd.
- In Congestion Avoidance, Linux only allows the cwnd to grow when the sender is unconstrained.
Before kernel version 3.16, this also applied to Slow Start.
The check for "unconstrained" is perfomed by checking if FlightSize is greater or equal to cwnd.
Since kernel version 3.16, which was published in August 2014, in Slow Start, the increase
implements rule #2 in {{rules}} in the `tcp_is_cwnd_limited` function in `tcp.h`.

### Assessment

Linux implements a limit to cwnd growth in accordance with rule #1 in {{rules}};
in Slow Start, this limit follows rule #2, while in Congestion Avoidance, it is more conservative than rule #2.
The specification and the ns-2 and ns-3 implementations are in conflict with rules #1 and #2 in {{rules}}.

## CUBIC

### Specification

{{Section 5.8 of !RFC9438}} says:

>Cubic doesn't increase cwnd when it's limited by the sending application or rwnd.

### Implementation

The description of Linux described in {{tcp-impl}} also applies to Cubic.

### Assessment

Both the specification and the Linux implementation limit the cwnd growth in accordance with rule #1 in {{rules}};
in Congestion Avoidance, this limit is more conservative than rule #2 in {{rules}},
and in Slow Start, it implements rule #2 in {{rules}}.

## SCTP

### Specification

{{Section 7.2.1 of !RFC9260}} says:

>When cwnd is less than or equal to ssthresh, an SCTP endpoint MUST use the slow-start algorithm to
increase cwnd only if the current congestion window is being fully utilized and the data sender
is not in Fast Recovery.
Only when these two conditions are met can the cwnd be increased; otherwise, the cwnd MUST NOT be increased.

### Assessment

The quoted statement from {{!RFC9260}} prescribes the same cwnd growth limitation that is also specified for Cubic and implemented for both Reno and Cubic in Linux.
It is in accordance with rule #1 in {{rules}}, and more conservative than rule #2 in {{rules}}.

{{Section 7.2.1 of !RFC9260}} is specifically limited to Slow Start.
Congestion Avoidance is discussed in {{Section 7.2.2 of !RFC9260}}
However, this section neither contains a similar rule, nor does it refer back to the rule that limits the growth of cwnd
in Section 7.2.1. It is thus implicitly clear that the quoted rule only applies to Slow Start, whereas the rules in {{rules}} apply to both Slow Start and Congestion Avoidance.

## QUIC

### Specification

{{Section 7.8 of !RFC9002}} states:

>When bytes in flight is smaller than the congestion window and sending is not pacing limited, the congestion window is underutilized. This can happen due to insufficient application data or flow control limits. When this occurs, the congestion window SHOULD NOT be increased in either slow start or congestion avoidance.

>A sender that paces packets might delay sending packets and not fully utilize the congestion window due to this delay. A sender SHOULD NOT consider itself application limited if it would have fully utilized the congestion window without pacing delay.

### Assessment

With the exception of pacing, this specification conservatively limits the growth in cwnd, similar to Cubic and SCTP.
The exception for pacing in the second paragraph requires that when pacing is enabled, it is specifically taken into account. Pacing could occur over various timescales, but
is typically done with delays below an RTT; thus, rule #2 in {{rules}} should cover this case.

## DCCP CCID2

### Specification

{{Section 5.1 of !RFC4341}} states:
>There are currently no standards governing TCP's use of the congestion window during an application-limited period.  In particular, it is possible for TCP's congestion window to grow quite large during a long uncongested period when the sender is application limited, sending at a low rate.  {{?RFC2861}} essentially suggests that TCP's congestion window not be increased during application-limited periods when the congestion window is not being fully utilized.

### Assessment

A DCCP Congestion Control ID (CCID) specifing TCP-like behaviour ought to follow the method specified in this document. The current guidance relates only to {{!RFC2861}}.
The text in {{Section 5.1 of !RFC4341}} is updated by this document to specify the management of the
cwnd during an application-limited period.


# Change Log

* -00 was the first individual submission for feedback by CCWG.
* -01 includes editorial improvements
   * Removes application interaction with QUIC pacing, since pacing might be within the QUIC stack.
   * Adds explicit mention of DCCP/CCID2.
   * Adds this change log.
