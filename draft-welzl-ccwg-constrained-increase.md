---
title: "Constrained Increase of the Congestion Window"
category: std

docname: draft-welzl-ccwg-constrained-increase-latest
submissiontype: IETF  # also: "independent", "editorial", "IAB", or "IRTF"
number:
date:
updates: RFC5681, RFC9438, RFC9260
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

normative:

informative:


--- abstract

This document specifies how transport protocols should increase their congestion window when the sender is constrained, either by the application stopping to supply data or by flow control.


--- middle

# Introduction

We call a sender "constrained" when the sender does not have data to send (i.e., the application has not provided enough data) even though the congestion control rules would allow it to, or when flow control limits apply (e.g., the receiver window (rwnd) in case of TCP).
RFCs specifying congestion control mechanisms diverge regarding the rules for increasing the congestion window (cwnd) when the sender is constrained.

This document specifies a uniform rule that MUST apply and gives a recommendation that congestion control implementations SHOULD follow.
An appendix gives an overview of the divergence in RFCs and some current implementations regarding constrained cwnd increase.

Different from {{?RFC5952}}, this document is solely concerned with the increase behavior. (should we discuss the relationship with this RFC some more?)

## Terminology

This document uses the terms defined in {{Section 2 of !RFC5681}}.

# Conventions and Definitions

{::boilerplate bcp14-tagged}


# Constrained cwnd Increase {#rules}

Senders of congestion controlled transport protocols:

1. MUST impose a limit on cwnd growth when FlightSize < cwnd.
2. SHOULD limit cwnd growth with inc(max(FlightSize)), where "inc" is the maximum unconstrained increase that would be carried out by the congestion control mechanism within one RTT, based on the "max(FlightSize)" parameter. For example, in case of Slow Start specified in {{!RFC5681}}, this limit is 2*max(FlightSize), and for Congestion Avoidance specified in {{!RFC5681}}, this limit is max(FlightSize)+1.

The maximum value to be used in the above rules is calculated as the maximum since the last time cwnd was decreased. If cwnd has never been decreased, it is the maximum since the beginning of the data transfer.

## Discussion

If the cwnd is limited for multiple RTTs, either by the application or by rwnd, continuously increasing it in every RTT causes a mismatch between cwnd and the capacity the path provides. Such unlimited increase is therefore disallowed by the first rule.

However, in most common congestion control mechanisms, a cwnd that has been fully utilized during a RTT grants an increase during the following RTT. Thus, such an increase is allowed by the second rule.


# Security Considerations

TODO Security


# IANA Considerations

This document has no IANA actions.


--- back

<!-- # Acknowledgments
{:numbered="false"}

TODO acknowledge. Note, numbered sections shouldn't appear
after an unnumbered one - so either move this last, or take
the numbering rule out. -->


# The state of RFCs and implementations

This section is meant as input for IETF discussion, and to be removed before publication.

## TCP ("Reno" congestion control)

### Specification

{{!RFC5681}} does not contain a rule to limit cwnd growth when the sender is constrained. This statement (page 8) even gives an impression that such cwnd growth may be expected:

>Implementation Note: An easy mistake to make is to simply use cwnd, rather than FlightSize, which in some implementations may incidentally increase well beyond rwnd.

{{?RFC7661}} also gives the impression that this is the expected TCP behavior (which {{?RFC7661}} changes), on page 4:

>Standard TCP does not impose additional restrictions on the growth of
the congestion window when a TCP sender is unable to send at the
maximum rate allowed by the cwnd. In this case, the rate-limited
sender may grow a cwnd far beyond that corresponding to the current
transmit rate, resulting in a value that does not reflect current
information about the state of the network path the flow is using.

### Implementation {#tcp-impl}

- ns-2 allows cwnd to grow in the face of a rwnd constraint. (Application-limited: not tested)
- ns-3 allows cwnd to grow in the face of either an application or rwnd constraint.
- Linux only allows cwnd to grow when the sender is unconstrained. Specifically, for Linux kernel 6.0.9, an increase is only allowed if a function called `tcp_is_cwnd_limited` in `tcp.h` yields `true`. This function checks the flag `tp->is_cwnd_limited`, which is initialised to `false` in `tcp_output.c` and later set to `true` only if FlightSize is greater or equal to cwnd (`is_cwnd_limited |= (tcp_packets_in_flight(tp) >= tcp_snd_cwnd(tp))`).

### Assessment

The specification, and the ns-2 and ns-3 implementations are in conflict with rules #1 and #2 in {{rules}}. Linux implements a limit in accordance with rule #1 in {{rules}}; this limit is more conservative than rule #2 in {{rules}}.

## CUBIC

### Specification

{{Section 5.8 of !RFC9438}} says: `Cubic doesn't increase cwnd when it's limited by the sending application or rwnd`.

### Implementation

- The limitation in Linux described in {{tcp-impl}} also applies to Cubic.

### Assessment

Both the specification and the Linux implementation limit cwnd growth in accordance with rule #1 in {{rules}}; this limit is more conservative than rule #2 in {{rules}}.


## SCTP

### Specification

{{!RFC9260}} to be discussed here.
