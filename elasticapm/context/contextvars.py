#  BSD 3-Clause License
#
#  Copyright (c) 2019, Elasticsearch BV
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  * Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from __future__ import absolute_import

import contextvars
from typing import TYPE_CHECKING

from elasticapm.context.base import BaseContext

if TYPE_CHECKING:
    import elasticapm.traces


class ContextVarsContext(BaseContext):
    elasticapm_transaction_var = contextvars.ContextVar("elasticapm_transaction_var")
    elasticapm_spans_var = contextvars.ContextVar("elasticapm_spans_var", default=())

    def get_transaction(self, clear: bool = False) -> "elasticapm.traces.Transaction":
        """
        Get the transaction for the current execution context

        If clear=True, also set the transaction to None for the current
        execution context.
        """
        try:
            transaction = self.elasticapm_transaction_var.get()
            if clear:
                self.set_transaction(None)
            return transaction
        except LookupError:
            return None

    def set_transaction(self, transaction: "elasticapm.traces.Transaction") -> None:
        """
        Set the transaction for the current execution context
        """
        self.elasticapm_transaction_var.set(transaction)

    def get_span(self) -> "elasticapm.traces.Span":
        """
        Get the active span for the current execution context.
        """
        spans = self.elasticapm_spans_var.get()
        return spans[-1] if spans else None

    def set_span(self, span: "elasticapm.traces.Span") -> None:
        """
        Set the active span for the current execution context.

        The previously-activated span will be saved to be re-activated later.
        """
        spans: tuple = self.elasticapm_spans_var.get() or ()
        self.elasticapm_spans_var.set(spans + (span,))

    def unset_span(self, clear_all: bool = False) -> "elasticapm.traces.Span":
        """
        De-activate the current span. If a span was previously active, it will
        become active again.

        Returns the deactivated span.

        If clear_all=True, all spans will be cleared and no span will be active.
        """
        spans = self.elasticapm_spans_var.get()
        span = None
        if spans:
            span = spans[-1]
            if clear_all:
                self.elasticapm_spans_var.set(())
            else:
                self.elasticapm_spans_var.set(spans[0:-1])
        return span


execution_context = ContextVarsContext()
