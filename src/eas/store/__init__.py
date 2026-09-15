"""Persistent context store (.eas/eas.db)."""

from eas.store.connection import Store, StoreError, ensure_store, is_context_enabled

__all__ = ["Store", "StoreError", "ensure_store", "is_context_enabled"]
