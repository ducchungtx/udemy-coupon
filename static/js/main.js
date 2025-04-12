/**
 * main.js - JavaScript chính cho Udemy Coupon Finder
 */
document.addEventListener('DOMContentLoaded', function () {
  // Lấy tham chiếu đến các phần tử DOM
  const urlInput = document.getElementById('url-input');
  const extractButton = document.getElementById('extract-button');
  const loadingDiv = document.getElementById('loading');
  const resultsDiv = document.getElementById('results');
  const courseCount = document.getElementById('course-count');
  const courseList = document.getElementById('course-list');
  const paginationControls = document.getElementById('pagination-controls');
  const perPageSelect = document.getElementById('per-page');
  const sortToggleBtn = document.getElementById('sort-toggle');
  const showingFrom = document.getElementById('showing-from');
  const showingTo = document.getElementById('showing-to');
  const totalItems = document.getElementById('total-items');
  const scrollToTop = document.getElementById('scroll-to-top');
  const searchInput = document.getElementById('search-input');
  const clearSearch = document.getElementById('clear-search');
  const searchResults = document.getElementById('search-results');

  // Pagination state
  let currentPage = 1;
  let itemsPerPage = parseInt(perPageSelect.value);
  let allCourses = [];
  let filteredCourses = []; // Thêm cho chức năng tìm kiếm
  let isReverseSorted = true; // Default is reversed (newest first)
  let searchTerm = ''; // Thêm cho chức năng tìm kiếm

  // Function to display a specific page of courses
  function displayPage(page, courses = null) {
    courseList.innerHTML = '';

    // Sử dụng danh sách đã lọc nếu đang tìm kiếm, nếu không thì dùng tất cả
    const displayCourses = courses || (searchTerm ? filteredCourses : allCourses);

    // Calculate start and end indices
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, displayCourses.length);

    // Update the showing info
    showingFrom.textContent = displayCourses.length > 0 ? startIndex + 1 : 0;
    showingTo.textContent = endIndex;
    totalItems.textContent = displayCourses.length;

    // Display courses for current page
    for (let i = startIndex; i < endIndex; i++) {
      const course = displayCourses[i];
      const courseItem = document.createElement('div');
      courseItem.className = 'p-4 hover:bg-gray-50 transition-colors';

      // Highlight search term in course title if searching
      let title = course.title;
      if (searchTerm) {
        // Tạo regex để highlight tất cả kết quả (case insensitive)
        const regex = new RegExp(searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
        title = title.replace(regex, match => `<span class="highlight">${match}</span>`);
      }

      courseItem.innerHTML = `
                <div class="mb-2">
                    <h3 class="font-medium text-gray-800">${title}</h3>
                </div>
                <a href="${course.url}" target="_blank"
                   class="inline-flex items-center text-sm px-3 py-1.5 bg-primary hover:bg-blue-600 text-white rounded-md transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
                    </svg>
                    Đăng ký miễn phí
                </a>
            `;
      courseList.appendChild(courseItem);
    }

    // Update pagination controls
    updatePaginationControls(displayCourses);
  }

  // Function to update pagination controls
  function updatePaginationControls(courses) {
    paginationControls.innerHTML = '';

    const displayCourses = courses || (searchTerm ? filteredCourses : allCourses);
    const totalPages = Math.ceil(displayCourses.length / itemsPerPage);

    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.innerHTML = '&laquo;';
    prevBtn.className = 'px-3 py-1 mx-1 border border-gray-300 rounded-md ' +
      (currentPage === 1 ? 'opacity-50 cursor-not-allowed bg-gray-100' : 'hover:bg-gray-100');
    prevBtn.disabled = currentPage === 1;
    prevBtn.addEventListener('click', () => {
      if (currentPage > 1) {
        currentPage--;
        displayPage(currentPage);
      }
    });
    paginationControls.appendChild(prevBtn);

    // Generate page buttons (with limit to avoid too many buttons)
    const maxButtons = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
    let endPage = Math.min(totalPages, startPage + maxButtons - 1);

    // Adjust start page if we're near the end
    if (endPage - startPage + 1 < maxButtons) {
      startPage = Math.max(1, endPage - maxButtons + 1);
    }

    // First page button if not visible in current range
    if (startPage > 1) {
      const firstBtn = document.createElement('button');
      firstBtn.textContent = '1';
      firstBtn.className = 'px-3 py-1 mx-1 border border-gray-300 rounded-md hover:bg-gray-100';
      firstBtn.addEventListener('click', () => {
        currentPage = 1;
        displayPage(currentPage);
      });
      paginationControls.appendChild(firstBtn);

      // Ellipsis if there's a gap
      if (startPage > 2) {
        const ellipsis = document.createElement('span');
        ellipsis.textContent = '...';
        ellipsis.className = 'mx-1 text-gray-500';
        paginationControls.appendChild(ellipsis);
      }
    }

    // Page number buttons
    for (let i = startPage; i <= endPage; i++) {
      const pageBtn = document.createElement('button');
      pageBtn.textContent = i;
      if (i === currentPage) {
        pageBtn.className = 'px-3 py-1 mx-1 bg-primary text-white border border-primary rounded-md';
      } else {
        pageBtn.className = 'px-3 py-1 mx-1 border border-gray-300 rounded-md hover:bg-gray-100';
      }
      pageBtn.addEventListener('click', () => {
        currentPage = i;
        displayPage(currentPage);
      });
      paginationControls.appendChild(pageBtn);
    }

    // Last page button if not visible in current range
    if (endPage < totalPages) {
      // Ellipsis if there's a gap
      if (endPage < totalPages - 1) {
        const ellipsis = document.createElement('span');
        ellipsis.textContent = '...';
        ellipsis.className = 'mx-1 text-gray-500';
        paginationControls.appendChild(ellipsis);
      }

      const lastBtn = document.createElement('button');
      lastBtn.textContent = totalPages;
      lastBtn.className = 'px-3 py-1 mx-1 border border-gray-300 rounded-md hover:bg-gray-100';
      lastBtn.addEventListener('click', () => {
        currentPage = totalPages;
        displayPage(currentPage);
      });
      paginationControls.appendChild(lastBtn);
    }

    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.innerHTML = '&raquo;';
    nextBtn.className = 'px-3 py-1 mx-1 border border-gray-300 rounded-md ' +
      (currentPage === totalPages || totalPages === 0 ? 'opacity-50 cursor-not-allowed bg-gray-100' : 'hover:bg-gray-100');
    nextBtn.disabled = currentPage === totalPages || totalPages === 0;
    nextBtn.addEventListener('click', () => {
      if (currentPage < totalPages) {
        currentPage++;
        displayPage(currentPage);
      }
    });
    paginationControls.appendChild(nextBtn);
  }

  // Function to toggle sort order
  function toggleSortOrder() {
    isReverseSorted = !isReverseSorted;
    allCourses.reverse();
    if (searchTerm) {
      filteredCourses.reverse();
    }
    currentPage = 1;
    displayPage(currentPage);
    sortToggleBtn.textContent = isReverseSorted ? 'Show Oldest First' : 'Show Newest First';
  }

  // Function to search courses
  function searchCourses(term) {
    searchTerm = term.trim().toLowerCase();

    if (searchTerm === '') {
      filteredCourses = [];
      searchResults.textContent = '';
      currentPage = 1;
      displayPage(currentPage);
      return;
    }

    // Filter courses based on search term
    filteredCourses = allCourses.filter(course =>
      course.title.toLowerCase().includes(searchTerm)
    );

    // Update search results count
    if (filteredCourses.length > 0) {
      searchResults.textContent = `Tìm thấy ${filteredCourses.length} khóa học phù hợp với "${searchTerm}"`;
    } else {
      searchResults.textContent = `Không tìm thấy khóa học nào phù hợp với "${searchTerm}"`;
    }

    // Reset to first page and display filtered results
    currentPage = 1;
    displayPage(currentPage, filteredCourses);
  }

  // Function to extract courses from a URL
  function extractCoursesFromUrl(url) {
    if (!url) return;

    // Reset search
    searchInput.value = '';
    searchTerm = '';
    filteredCourses = [];
    searchResults.textContent = '';

    // Fill the input field with the URL
    urlInput.value = url;

    // Show loading indicator
    loadingDiv.style.display = 'block';
    resultsDiv.style.display = 'none';
    courseList.innerHTML = '';

    // Scroll to the top of the page
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Fetch courses from API
    fetch(`/api/extract-courses?url=${encodeURIComponent(url)}`)
      .then(response => response.json())
      .then(data => {
        loadingDiv.style.display = 'none';
        resultsDiv.style.display = 'block';

        courseCount.textContent = data.count;

        if (data.courses && data.courses.length > 0) {
          // Store all courses
          allCourses = data.courses;

          // Default is reversed (newest first)
          if (isReverseSorted) {
            allCourses.reverse();
          }

          // Reset to first page and display
          currentPage = 1;
          displayPage(currentPage);
        } else {
          courseList.innerHTML = '<div class="p-8 text-center text-gray-500">Không tìm thấy khóa học nào trên trang này.</div>';
          paginationControls.innerHTML = '';
          showingFrom.textContent = '0';
          showingTo.textContent = '0';
          totalItems.textContent = '0';
          searchResults.textContent = '';
        }
      })
      .catch(error => {
        loadingDiv.style.display = 'none';
        courseList.innerHTML = `<div class="p-8 text-center text-red-500">Lỗi khi trích xuất khóa học: ${error.message}</div>`;
        resultsDiv.style.display = 'block';
        paginationControls.innerHTML = '';
        showingFrom.textContent = '0';
        showingTo.textContent = '0';
        totalItems.textContent = '0';
        searchResults.textContent = '';
      });
  }

  // Event listeners

  // Event listener for search input
  searchInput.addEventListener('input', function () {
    searchCourses(this.value);
  });

  // Event listener for clear search button
  clearSearch.addEventListener('click', function () {
    searchInput.value = '';
    searchTerm = '';
    filteredCourses = [];
    searchResults.textContent = '';
    currentPage = 1;
    displayPage(currentPage);
  });

  // Event listener for sort toggle
  sortToggleBtn.addEventListener('click', toggleSortOrder);
  sortToggleBtn.textContent = isReverseSorted ? 'Show Oldest First' : 'Show Newest First';

  // Event listener for items per page change
  perPageSelect.addEventListener('change', function () {
    itemsPerPage = parseInt(this.value);
    currentPage = 1;
    displayPage(currentPage);
  });

  // Extract courses button handler
  extractButton.addEventListener('click', function () {
    const url = urlInput.value.trim();
    extractCoursesFromUrl(url);
  });

  // Add click handler to all coupon boxes
  const couponBoxes = document.querySelectorAll('.coupon-box');
  couponBoxes.forEach(box => {
    box.addEventListener('click', function () {
      const url = this.getAttribute('data-url');
      extractCoursesFromUrl(url);
    });
  });

  // Scroll to top button functionality
  window.addEventListener('scroll', function () {
    if (window.pageYOffset > 300) {
      scrollToTop.style.display = 'block';
    } else {
      scrollToTop.style.display = 'none';
    }
  });

  scrollToTop.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
});