#include "fls/reader/reader.hpp"                  //
#include "fls/connection.hpp"                     // for Connector (ptr only)
#include "fls/cor/lyt/buf.hpp"                    // for Buf
#include "fls/csv/csv.hpp"                        // for CSV
#include "fls/encoder/materializer.hpp"           //
#include "fls/expression/decoding_operator.hpp"   //
#include "fls/expression/encoding_operator.hpp"   //
#include "fls/expression/expression_executor.hpp" //
#include "fls/expression/interpreter.hpp"         // for Interpreter
#include "fls/expression/physical_expression.hpp" // for PhysicalExpr
#include "fls/expression/predicate_operator.hpp"  //
#include "fls/footer/rowgroup_descriptor.hpp"     // for Footer, ColumnMeta...
#include "fls/io/file.hpp"                        // for File
#include "fls/io/io.hpp"                          // for IO, io
#include "fls/json/nlohmann/json.hpp"             // for json
#include "fls/reader/column_view.hpp"
#include "fls/table/chunk.hpp" // for Chunk
#include <filesystem>          // for operator/, path
#include <memory>              // for make_unique, uniqu...
#include <string>              // for basic_string

namespace fastlanes {
Reader::Reader(const path& dir_path, Connection& fls) {
	// read footer
	{ m_footer = make_rowgroup_descriptor(dir_path / FOOTER_FILE_NAME); }

	// read file
	{
		// allocate buffer
		m_buf = make_unique<Buf>(m_footer->m_rowgroup_size);       // todo[memory_pool]
		io io = make_unique<File>(dir_path / FASTLANES_FILE_NAME); // todo[IO]
		IO::read(io, *m_buf);
		m_rowgroup_view = make_unique<RowgroupView>(m_buf->Span(), *m_footer);
	}

	// init level 1 expression
	{
		m_expressions.reserve(m_footer->size());
		for (n_t col_idx {0}; col_idx < m_footer->size(); ++col_idx) {
			auto& column_descriptor = m_footer->m_column_descriptors[col_idx];
			auto& column_view       = (*m_rowgroup_view)[col_idx];

			InterpreterState state;
			auto             physical_expr = make_decoding_expression(column_descriptor, column_view, *this, state);
			ExprExecutor::CountOperator(*physical_expr);
			m_expressions.emplace_back(physical_expr);
		}
	}
}

vector<sp<PhysicalExpr>>& Reader::get_chunk(const n_t vec_idx) {
	for (n_t col_idx {0}; col_idx < m_footer->size(); ++col_idx) {
		auto& physical_expr = *m_expressions[col_idx];
		ExprExecutor::smart_execute(physical_expr, vec_idx);
	}
	return m_expressions;
}

void Reader::reset() {
	m_footer.reset();
	m_buf.reset();
	m_rowgroup_view.reset();
}

up<Rowgroup> Reader::materialize() {
	auto               rowgroup_up = std::make_unique<Rowgroup>(*m_footer);
	const Materializer materializer {*rowgroup_up};

	for (n_t vec_idx {0}; vec_idx < m_footer->m_n_vec; vec_idx++) {
		auto& expressions = get_chunk(vec_idx);
		materializer.Materialize(expressions, vec_idx);
	};

	// materializer.rowgroup.Cast();
	materializer.rowgroup.Finalize();
	materializer.rowgroup.GetStatistics();

	return rowgroup_up;
}

void Reader::to_csv(const path& dir_path) {
	const auto& materialized_rowgroup = materialize();
	CSV::to_csv(dir_path, *materialized_rowgroup);
}

RowgroupDescriptor& Reader::footer() const {
	return *m_footer;
}

vector<string> Reader::get_column_names() const {
	if (m_footer == nullptr) {
		throw std::runtime_error("Footer is initialized");
	}

	return m_footer->GetColumnNames();
}

vector<DataType> Reader::get_data_types() const {
	if (m_footer == nullptr) {
		throw std::runtime_error("Footer is initialized");
	}

	return m_footer->GetDataTypes();
}

} // namespace fastlanes