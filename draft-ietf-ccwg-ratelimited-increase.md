---
title: "Increase of the Congestion Window when the Sender Is Rate-Limited"
abbrev: "Rate-Limited cwnd Increase"
category: std

docname: draft-ietf-ccwg-ratelimited-increase-latest
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
  github: "mwelzl/draft-ccwg-ratelimited-increase"
  latest: "https://mwelzl.github.io/draft-ccwg-ratelimited-increase/draft-ietf-ccwg-ratelimited-increase.html"

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
    org: University of Washington
    street: Campus Box 352500
    street: 185 Stevens Way
    city: Seattle, WA 98195
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
  -
    ins: M. P. Tahiliani
    name: Mohit P. Tahiliani
    org: National Institute of Technology Karnataka
    street: Department of Computer Science and Engineering
    street: P. O. Srinivasnagar, Surathkal
    city: Mangalore, Karnataka - 575025
    country: India
    email: tahiliani@nitk.edu.in
    uri: https://tahiliani.in/

normative:

informative:
I-D.ietf-ccwg-bbr:


--- abstract

This document specifies how transport protocols increase their congestion window when the sender is rate-limited, and updates RFC 5681, RFC 9002, RFC 9260, and RFC 9438.
Such a limitation can be caused by the sending application not supplying data or by receiver flow control.


--- middle

# Introduction

A sender of a congestion controlled transport protocol becomes "rate-limited" when it does not send any data
even though the congestion control rules would allow it to transmit data.
This could occur because the application has not provided sufficient data to fully utilise the congestion window (cwnd).
It could also occur because the receiver has limited the sender using flow control
(e.g., by the advertised TCP receiver window (rwnd) or by the connection or stream flow credit in QUIC).
Current RFCs specifying congestion control algorithms diverge regarding the rules for increasing the cwnd when the sender is rate-limited.

Congestion Window Validation (CWV) {{!RFC7661}} provides an experimental specification defining how to manage a cwnd that has
become larger than the current flight size, and how to respond to detected congestion when this is the case.
In contrast, this present document concerns the increase in cwnd when a sender is rate-limited. These two topics are distinct,
but are related, because both describe the management of the cwnd when a sender does not fully utilise the current cwnd.

An appendix provides an overview of the divergence in current RFCs and some current implementations regarding cwnd increase when the sender is rate-limited.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

## Terminology

This document uses the terms defined in {{Section 2 of !RFC5681}} and {{Section 3 of !RFC7661}}. Additionally, we define:

- maxFS: the largest value of FlightSize since the last time that cwnd was decreased. If cwnd has never been decreased, maxFS is the maximum value of FlightSize since the start of the data transfer. Upon a reduction in the cwnd (for any reason), the maxFS is reset to zero. This results in a maxFS value that reflects the first FlightSize measurement taken after the cwnd reduction.
- initcwnd: The initial value of the congestion window, also known as the "initial window" ("IW" in {{!RFC5681}}).

# Increase rules {#rules}

This document specifies a uniform rule that congestion control algorithms MUST apply and provides a recommendation that congestion control implementations ought to follow.

When FlightSize < cwnd, regardless of the current state of a congestion control algorithm, the following rules apply for senders using a congestion controlled transport protocol:

1. The sender MUST initialise the maxFS parameter to initcwnd when the congestion control algorithm is started or restarted. Thereafter when the FlightSize is updated, the sender updates maxFS:

~~~
maxFS = max(FlightSize, maxFS)
~~~

The sender MUST reset the maxFS parameter to initcwnd after any adjustment that reduces the cwnd. It will then track the current FlightSize.


2. The sender MUST cap cwnd to be no larger than limit(maxFS).

In rule #1, the function limit() returns the maximum cwnd value the congestion control algorithm would yield by increasing for every ACK that acknowledges bytes in flight, starting from the value of the maxFS parameter.
For example, for Slow Start, as specified in {{!RFC5681}}, limit(maxFS)=2*maxFS, such that equation 2 in {{!RFC5681}} becomes:

~~~
cwnd_new = cwnd + min (N, SMSS)
cwnd = min(cwnd_new, 2*maxFS)
~~~
where cwnd and SMSS follow their definitions in {{!RFC5681}} and N is the number of previously unacknowledged bytes acknowledged in the incoming ACK.

Similarly, with rule #1 applied to Congestion Avoidance, limit(maxFS)=SMSS+maxFS, such that equation 3 in {{!RFC5681}} becomes:

~~~
cwnd_new = cwnd + SMSS*SMSS/cwnd
cwnd = min(cwnd_new, SMSS+maxFS)
~~~
where cwnd and SMSS follow their definitions in {{!RFC5681}}.

NOTE: This specification defines the current method used to increase the cwnd for a rate-limited sender. Without a way to reduce cwnd when the transport sender becomes rate-limited, rule #1 allows maxFS to stay valid for a long time, possibly not reflecting the reality of the end-to-end Internet path in use. This is remedied by "Congestion Window Validation" in {{!RFC7661}}, which also defines a "pipeACK" variable that measures the recently acknowledged size of the network pipe when the sender was rate-limited.

## Example
We illustrate the working of rule #1 by showing the increase of cwnd in two scenarios: when the growth of cwnd is unconstrained, and when the rate-limited sender is constrained by the increase rule. In both cases, we assume the initial cwnd (initcwnd) = 10 segments, as defined for TCP in {{?RFC6928}} and QUIC in {{?RFC9002}}, a single connection begins with Slow Start, the sender transmits a total of 14 segments but pauses after transmitting 10 segments and resumes the transmission for the remaining 4 segments afterwards, no packets are lost, and an ACK is sent for every packet.

### Unconstrained sender
Initially, cwnd = initcwnd. Therefore, using initcwnd = 10 segments, the sender transmits 10 segments and pauses. Since the sender is in the Slow Start phase, the arrival of an each ACK for the 10 sent segments increases the cwnd by 1 segment, resulting in the cwnd increasing to 20 segments. Subsequently, after the pause, the sender transmits 4 segments and pauses again. As a consequence, the arrival of 4 ACKs results in cwnd further increasing to 24 segments, even though the sender is rate-limited (i.e., has never sent more than 10 segments/RTT).

### Sender constrained by the increase rules
For simplicity, this example accounts for the cwnd in segments, rather than bytes.
Initially, cwnd = initcwnd. Therefore, using initcwnd = 10 segments, the sender transmits 10 segments and pauses; note that FlightSize and maxFS are both 10 segments at this point. Since the sender is in the Slow Start phase, the arrival of each ACK for the 10 sent segments increases the cwnd by 1 segment, resulting in the cwnd increasing to 20 segments. Subsequently, when the sender resumes and transmits 4 new segments, rule #1 constrains the growth of the cwnd because FlightSize < cwnd and therefore this caps the cwnd to be no larger than limit(maxFS) = 2 X maxFS = 2 X 10 segments = 20 segments.

## Discussion

If the sending rate is less than the rate permitted by the cwnd for multiple RTTs, limited either by the sending application or by the receiver-advertised window, a continuous increase in the cwnd would cause a mismatch between the cwnd and the capacity that the path supports (i.e., over-estimating the capacity).
Such unlimited growth in the cwnd is therefore disallowed.

However, in most common congestion control algorithms, in the absence of an indication of congestion, a cwnd that has been fully utilized during an RTT (where a sender was cwnd-limited) permits the cwnd to be increased during the immediately following RTT. This increase is allowed by rule #1.


### Rate-based congestion control

The present document updates congestion control specifications that use a cwnd to limit the number of unacknowledged bytes (or packets) that a sender is allowed to emit. Use of a cwnd variable to control sending rate is not the only mechanism available and not the only mechanism that is used in practice.

Congestion control algorithms can also constrain data transmission by explicitly calculating the sending rate over some time interval, by "pacing" packets (injecting pauses in between their transmission) or via combinations of the above (e.g., BBR combines these three methods {{?I-D.ietf-ccwg-bbr}}). The guiding principle behind rule #1 applies to all congestion control algorithms: in the absence of a congestion indication, a sender is allowed to increase its rate from the amount of data that it has transmitted during the previous RTT. This holds irrespective of whether the sender is rate-limited or not.


### Pacing

Pacing mechanisms seek to avoid the negative impacts associated with "bursts" (flights of packets transmitted back-to-back). The present specification introduces a limit using "maxFS"; thus, as long as the number of packets per RTT is unaffected by pacing, rule #1 also does not constrain the use of pacing mechanisms.


# Security Considerations

While congestion control designs could result in unwanted competing traffic, they do not directly result in new security considerations.

The security considerations are the same as for other
   congestion control methods.  Such methods rely on the receiver
   appropriately acknowledging receipt of data.  The ability of an on-
   path or off-path attacker to influence congestion control depends
   upon the security properties of the transport protocol being used.
Transport protocols that provide authentication (including those using encryption), or are carried over protocols that provide authentication,
can protect their congestion control algorithm from network attack. This is orthogonal to the specification of congestion control rules.

# IANA Considerations

This document requests no IANA action.


--- back


# The state of RFCs and implementations

This section is provided as input for IETF discussion, and should be removed before publication.

## TCP ("Reno" congestion control)

### Specification

{{!RFC7661}} suggests there is no increase limitation in the standard TCP behavior (which {{!RFC7661}} changes), on page 4:

>Standard TCP does not impose additional restrictions on the growth of
the congestion window when a TCP sender is unable to send at the
maximum rate allowed by the cwnd. In this case, the rate-limited
sender may grow a cwnd far beyond that corresponding to the current
transmit rate, resulting in a value that does not reflect current
information about the state of the network path the flow is using.

### Implementation {#tcp-impl}

- ns-2 allows cwnd to grow when it is rate-limited by rwnd. (Rate-limited by the sending application: not tested.)
- Until release 3.42, ns-3 allowed cwnd to grow when rate-limited, either due to an application or rwnd limit.  Since release 3.42, ns-3 TCP models conform to rule #1 in {{rules}}, following the current Linux TCP approach in this regard (see next bullet).
- In Congestion Avoidance, Linux only allows the cwnd to grow when the sender is unconstrained.
Before kernel version 3.16, this also applied to Slow Start.
The check for "unconstrained" is perfomed by checking if FlightSize is greater or equal to cwnd.
Since kernel version 3.16, which was published in August 2014, in Slow Start, the increase
implements rule #1 in {{rules}} in the `tcp_is_cwnd_limited` function in `tcp.h`.

### Assessment

Linux implements a limit to cwnd growth in accordance with rule #1 in {{rules}};
in Slow Start, this limit follows the rule's upper limit, while in Congestion Avoidance, it is more conservative than rule #1.
The specification and the ns-2 and (older) ns-3 implementations are in conflict with rule #1 in {{rules}}.

## CUBIC

### Specification

{{Section 5.8 of !RFC9438}} says:

>Cubic doesn't increase cwnd when it's limited by the sending application or rwnd.

### Implementation

The description of Linux described in {{tcp-impl}} also applies to Cubic.

### Assessment

Both the specification and the Linux implementation limit the cwnd growth in accordance with rule #1 in {{rules}};
in Congestion Avoidance, this limit is more conservative than rule #1 in {{rules}},
and in Slow Start, it implements the upper limit of rule #1.

## The Stream Control Transmission Protocol (SCTP)

### Specification

{{Section 7.2.1 of !RFC9260}} says:

>When cwnd is less than or equal to ssthresh, an SCTP endpoint MUST use the slow-start algorithm to
increase cwnd only if the current congestion window is being fully utilized and the data sender
is not in Fast Recovery.
Only when these two conditions are met can the cwnd be increased; otherwise, the cwnd MUST NOT be increased.

### Assessment

The quoted statement from {{!RFC9260}} prescribes the same cwnd growth limitation that is also specified for Cubic and implemented for both Reno and Cubic in Linux.
It is in accordance with rule #1 in {{rules}}, and more conservative.

{{Section 7.2.1 of !RFC9260}} is specifically limited to Slow Start.
Congestion Avoidance is discussed in {{Section 7.2.2 of !RFC9260}}
However, this section neither contains a similar rule, nor does it refer back to the rule that limits the growth of cwnd
in Section 7.2.1. It is thus implicitly clear that the quoted rule only applies to Slow Start, whereas the rules in {{rules}} apply to both Slow Start and Congestion Avoidance.

## The QUIC Transport Protocol

### Specification

{{Section 7.8 of !RFC9002}} states:

>When bytes in flight is smaller than the congestion window and sending is not pacing limited, the congestion window is underutilized. This can happen due to insufficient application data or flow control limits. When this occurs, the congestion window SHOULD NOT be increased in either slow start or congestion avoidance.

### Assessment

With the exception of pacing, this specification conservatively limits the growth in cwnd, similar to Cubic and SCTP. It is in accordance with rule #1 in {{rules}}, and more conservative.

## The Datagram Congestion Control Protocol (DCCP) CCID2

### Specification

{{Section 5.1 of ?RFC4341}} states:
>There are currently no standards governing TCP's use of the congestion window during an application-limited period.  In particular, it is possible for TCP's congestion window to grow quite large during a long uncongested period when the sender is application limited, sending at a low rate.  {{?RFC2861}} essentially suggests that TCP's congestion window not be increased during application-limited periods when the congestion window is not being fully utilized.

### Assessment

A DCCP Congestion Control ID (CCID) specifing TCP-like behaviour ought to follow the method specified in this document. The current guidance relates only to {{?RFC2861}}.
The text in {{Section 5.1 of ?RFC4341}} is updated by this document to specify the management of the
cwnd when the sender is rate-limited.


# Change Log

* -00 was the first individual submission for feedback by CCWG.
* -01 includes editorial improvements
   * Removes application interaction with QUIC pacing, since pacing might be within the QUIC stack.
   * Adds explicit mention of DCCP/CCID2.
   * Adds this change log.
* -02 addresses comments from IETF-119
   * Discusses rate-based controls and pacing.
   * Trims the list of possible RFCs to update.
   * Some editorial fixes: "congestion control algorithm" instead of "mechanism" for consistency with RFC5033.bis; earlier definition of maxFS; explicit mention of RFCs to update in abstract.
* -03 addresses comments from IETF-120
   * Introduces a third rule, with MAY, that avoids having an unvalidated long-lived maxFS (using pipeACK from RFC 7661).
   * Changes "inc" to "limit" and adapts the wording of rule 2 to make it clearer (thanks to Neal Cardwell).
   * Appendix: updates ns-3 in line with the recent implementation.
   * Appendix: makes the RFC 9002 text clearer and shorter.
* draft-ietf-ccwg-ratelimited-increase-00
   * adds Mohit Tahiliani as a co-author
   * refines the "rule" text (shorter, clearer)
   * adds an example
* draft-ietf-ccwg-ratelimited-increase-01
  * Clarified what we mean with an RTT
  * rephrased example regarding initcwnd, citing RFCs 6928 and 9002
  * removed the too vague rule 1 and made rule 2 (now rule 1) a MUST
* draft-ietf-ccwg-ratelimited-increase-02
  * Improved the last sentence of section 3.1.2.
  * Removed a confusing and unnecessary sentence about pacing (as suggested at IETF-123).
* draft-ietf-ccwg-ratelimited-increase-03
  * The editors checked rule 2, and found that rule 1 was sufficient, and did not depend on the ordering of rules in newCWV (RFC7661), hence rule 2 was finally removed.
  * Cleaned language and improved text explaining how this compliments RFC7661.
  * Checked/updated definitions.


# Acknowledgments
{:numbered="false"}

The authors would like to thank Neal Cardwell and Martin Duke for suggesting improvements to this document.
