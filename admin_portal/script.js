document.addEventListener('DOMContentLoaded', function() {
  // Get DOM elements
  const queryForm = document.getElementById('query-form');
  const naturalQuery = document.getElementById('natural-query');
  const sqlQuery = document.getElementById('sql-query');
  const resultsContainer = document.getElementById('results-table-container');
  const errorMessage = document.getElementById('error-message');
  const loadingIndicator = document.getElementById('loading');

  // Add form submit event listener
  queryForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Reset previous results and show loading state
    errorMessage.innerText = '';
    sqlQuery.innerText = 'Processing...';
    resultsContainer.innerHTML = '';
    loadingIndicator.style.display = 'block';

    const query = naturalQuery.value.trim();
    
    if (!query) {
      showError('Please enter a query');
      return;
    }

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
      });

      const data = await response.json();
      
      // Hide loading indicator
      loadingIndicator.style.display = 'none';

      if (response.ok) {
        // Display the SQL query
        sqlQuery.innerText = data.sql_query;
        
        // Create and display the results table
        if (data.results && data.results.length > 0) {
          createResultsTable(data.columns, data.results);
        } else {
          resultsContainer.innerHTML = '<p class="placeholder-text">No results found for this query.</p>';
        }
      } else {
        showError(data.error || 'An error occurred while processing your query');
        sqlQuery.innerText = 'SQL query will appear here...';
      }
    } catch (error) {
      console.error('Error:', error);
      loadingIndicator.style.display = 'none';
      showError('A network error occurred. Please try again.');
      sqlQuery.innerText = 'SQL query will appear here...';
    }
  });

  // Function to create the results table
  function createResultsTable(columns, results) {
    const table = document.createElement('table');
    
    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    columns.forEach(column => {
      const th = document.createElement('th');
      th.textContent = column;
      headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create table body
    const tbody = document.createElement('tbody');
    
    results.forEach(row => {
      const tr = document.createElement('tr');
      
      columns.forEach(column => {
        const td = document.createElement('td');
        td.textContent = row[column] !== null ? row[column] : 'NULL';
        tr.appendChild(td);
      });
      
      tbody.appendChild(tr);
    });
    
    table.appendChild(tbody);
    resultsContainer.innerHTML = '';
    resultsContainer.appendChild(table);
  }

  // Function to show error message
  function showError(message) {
    errorMessage.innerText = message;
    loadingIndicator.style.display = 'none';
  }
});