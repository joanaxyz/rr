class Paginator {
    constructor(items, itemsPerPage = 5) {
        this.items = items;
        this.itemsPerPage = itemsPerPage;
        this.currentPage = 1;
        this.updateTotalPages();
    }

    updateTotalPages() {
        this.totalPages = Math.ceil(this.items.length / this.itemsPerPage) || 1;
        if (this.currentPage > this.totalPages) {
            this.currentPage = this.totalPages;
        }
    }

    setItems(items) {
        this.items = items;
        // Reset to page 1 when items change (standard UX - when filtering, show first page)
        this.currentPage = 1;
        this.updateTotalPages();
        // Ensure we're on a valid page (safety check)
        if (this.currentPage > this.totalPages) {
            this.currentPage = Math.max(1, this.totalPages);
        }
    }

    getCurrentPageItems() {
        const start = (this.currentPage - 1) * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        return this.items.slice(start, end);
    }

    goToPage(pageNum) {
        const page = Math.max(1, Math.min(pageNum, this.totalPages));
        this.currentPage = page;
        return this.getCurrentPageItems();
    }

    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.currentPage++;
        }
        return this.getCurrentPageItems();
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
        }
        return this.getCurrentPageItems();
    }

    hasNextPage() {
        return this.currentPage < this.totalPages;
    }

    hasPreviousPage() {
        return this.currentPage > 1;
    }
}
