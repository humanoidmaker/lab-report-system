import { useState, useEffect } from 'react';
import api from '../utils/api';
import toast from 'react-hot-toast';
import { Search, X, FileText, CheckCircle, Printer, Download, Shield } from 'lucide-react';

export default function Reports() {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQ, setSearchQ] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [verifying, setVerifying] = useState(false);

  useEffect(() => { loadReports(); }, [statusFilter]);

  const loadReports = async () => {
    setLoading(true);
    try {
      const params: any = { limit: 200 };
      if (statusFilter) params.status = statusFilter;
      if (searchQ) params.q = searchQ;
      const { data } = await api.get('/reports', { params });
      setReports(data.data || []);
    } catch {
      toast.error('Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (id: string) => {
    setVerifying(true);
    try {
      await api.put(`/reports/${id}/verify`);
      toast.success('Report verified');
      if (selectedReport?.id === id) {
        setSelectedReport({ ...selectedReport, status: 'verified' });
      }
      loadReports();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Verification failed');
    } finally {
      setVerifying(false);
    }
  };

  const handlePrint = async (id: string) => {
    try {
      const response = await api.get(`/reports/${id}/pdf`, { responseType: 'blob' });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      window.open(url, '_blank');
    } catch {
      // Fallback: open print-friendly view
      if (selectedReport) {
        const printWindow = window.open('', '_blank');
        if (printWindow) {
          printWindow.document.write(generatePrintHTML(selectedReport));
          printWindow.document.close();
          printWindow.onload = () => printWindow.print();
        }
      }
    }
  };

  const generatePrintHTML = (report: any) => {
    const results = report.results || [];
    const rows = results.map((r: any) =>
      `<tr style="${r.is_abnormal ? 'color: red; font-weight: bold;' : ''}">
        <td style="padding: 6px 12px; border: 1px solid #ddd;">${r.parameter_name}</td>
        <td style="padding: 6px 12px; border: 1px solid #ddd;">${r.value}</td>
        <td style="padding: 6px 12px; border: 1px solid #ddd;">${r.unit || ''}</td>
        <td style="padding: 6px 12px; border: 1px solid #ddd;">${r.reference_range || ''}</td>
      </tr>`
    ).join('');

    return `<!DOCTYPE html><html><head><title>${report.report_number}</title></head><body style="font-family: Arial, sans-serif; padding: 40px; max-width: 800px; margin: 0 auto;">
      <div style="text-align: center; border-bottom: 2px solid #1e3a5f; padding-bottom: 20px; margin-bottom: 20px;">
        <h1 style="color: #1e3a5f; margin: 0;">Lab Report</h1>
        <p style="color: #666; margin: 5px 0;">${report.report_number}</p>
      </div>
      <table style="width: 100%; margin-bottom: 20px;"><tr>
        <td><strong>Patient:</strong> ${report.patient_name}<br/><strong>Test:</strong> ${report.test_name}</td>
        <td style="text-align: right;"><strong>Date:</strong> ${new Date(report.created_at).toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata' })}<br/><strong>Status:</strong> ${report.status}</td>
      </tr></table>
      <table style="width: 100%; border-collapse: collapse;">
        <thead><tr style="background: #f5f5f5;"><th style="padding: 8px 12px; border: 1px solid #ddd; text-align: left;">Parameter</th><th style="padding: 8px 12px; border: 1px solid #ddd; text-align: left;">Value</th><th style="padding: 8px 12px; border: 1px solid #ddd; text-align: left;">Unit</th><th style="padding: 8px 12px; border: 1px solid #ddd; text-align: left;">Reference Range</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
      ${report.technician_name ? `<p style="margin-top: 30px; color: #666;">Technician: ${report.technician_name}</p>` : ''}
      ${report.status === 'verified' ? '<p style="color: green; font-weight: bold; margin-top: 10px;">VERIFIED</p>' : ''}
    </body></html>`;
  };

  const openReport = async (report: any) => {
    setSelectedReport(report);
    // Try to fetch full report with results
    try {
      const { data } = await api.get(`/reports/${report.id}`);
      setSelectedReport(data.data || data || report);
    } catch {
      // Use what we have
    }
  };

  const filtered = reports.filter((r) => {
    const q = searchQ.toLowerCase();
    return (r.report_number || '').toLowerCase().includes(q) ||
      (r.patient_name || '').toLowerCase().includes(q) ||
      (r.test_name || '').toLowerCase().includes(q);
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Reports</h1>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
          <input
            className="input-field pl-9"
            placeholder="Search by report #, patient, or test..."
            value={searchQ}
            onChange={(e) => setSearchQ(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && loadReports()}
          />
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="input-field w-auto">
          <option value="">All Status</option>
          <option value="pending_verification">Pending Verification</option>
          <option value="verified">Verified</option>
        </select>
      </div>

      {/* Report List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin h-8 w-8 border-4 border-accent-500 border-t-transparent rounded-full" />
        </div>
      ) : filtered.length > 0 ? (
        <div className="card p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Report #</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Patient</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500 hidden sm:table-cell">Test</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500 hidden md:table-cell">Date</th>
                <th className="text-left py-3 px-4 font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((r) => (
                <tr key={r.id} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 font-medium text-primary-600">{r.report_number}</td>
                  <td className="py-3 px-4">{r.patient_name}</td>
                  <td className="py-3 px-4 hidden sm:table-cell">{r.test_name}</td>
                  <td className="py-3 px-4">
                    <span className={r.status === 'verified' ? 'badge-verified' : 'badge-pending'}>
                      {r.status === 'verified' ? 'Verified' : 'Pending'}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-500 hidden md:table-cell">
                    {new Date(r.created_at).toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata' })}
                  </td>
                  <td className="py-3 px-4 space-x-2">
                    <button onClick={() => openReport(r)} className="text-accent-600 hover:underline text-xs font-medium">View</button>
                    {r.status !== 'verified' && (
                      <button onClick={() => handleVerify(r.id)} className="text-green-600 hover:underline text-xs font-medium">Verify</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="card py-12 text-center">
          <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="text-gray-400 text-sm">No reports found</p>
        </div>
      )}

      {/* Report Detail Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold text-primary-600">{selectedReport.report_number}</h2>
                <p className="text-sm text-gray-500">
                  {selectedReport.patient_name} | {selectedReport.test_name}
                </p>
              </div>
              <button onClick={() => setSelectedReport(null)}><X className="w-5 h-5" /></button>
            </div>

            {/* Report Info */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4 p-3 bg-gray-50 rounded-lg text-sm">
              <div>
                <span className="text-gray-400 block text-xs">Patient</span>
                <span className="font-medium">{selectedReport.patient_name}</span>
              </div>
              <div>
                <span className="text-gray-400 block text-xs">Test</span>
                <span className="font-medium">{selectedReport.test_name}</span>
              </div>
              <div>
                <span className="text-gray-400 block text-xs">Date</span>
                <span className="font-medium">{new Date(selectedReport.created_at).toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata' })}</span>
              </div>
              <div>
                <span className="text-gray-400 block text-xs">Status</span>
                <span className={`font-medium ${selectedReport.status === 'verified' ? 'text-green-600' : 'text-amber-600'}`}>
                  {selectedReport.status === 'verified' ? 'Verified' : 'Pending Verification'}
                </span>
              </div>
            </div>

            {/* Results Table */}
            {(selectedReport.results || []).length > 0 ? (
              <div className="overflow-x-auto mb-4">
                <table className="w-full text-sm border">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="text-left py-2.5 px-3 font-medium text-gray-500 border-b">Parameter</th>
                      <th className="text-left py-2.5 px-3 font-medium text-gray-500 border-b">Value</th>
                      <th className="text-left py-2.5 px-3 font-medium text-gray-500 border-b">Unit</th>
                      <th className="text-left py-2.5 px-3 font-medium text-gray-500 border-b">Reference Range</th>
                      <th className="text-center py-2.5 px-3 font-medium text-gray-500 border-b">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedReport.results.map((r: any, i: number) => (
                      <tr key={i} className={`border-b ${r.is_abnormal ? 'bg-red-50' : ''}`}>
                        <td className="py-2.5 px-3 font-medium text-gray-700">{r.parameter_name}</td>
                        <td className={`py-2.5 px-3 font-semibold ${r.is_abnormal ? 'text-red-700' : 'text-gray-900'}`}>
                          {r.value}
                        </td>
                        <td className="py-2.5 px-3 text-gray-500">{r.unit || '-'}</td>
                        <td className="py-2.5 px-3 text-gray-400">{r.reference_range || '-'}</td>
                        <td className="py-2.5 px-3 text-center">
                          {r.is_abnormal ? (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700 font-medium">Abnormal</span>
                          ) : (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium">Normal</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-6 text-center text-gray-400 text-sm border rounded-lg mb-4">
                No detailed results available
              </div>
            )}

            {selectedReport.technician_name && (
              <p className="text-xs text-gray-400 mb-4">Technician: {selectedReport.technician_name}</p>
            )}

            {/* Actions */}
            <div className="flex gap-3 justify-end border-t pt-4">
              {selectedReport.status !== 'verified' && (
                <button onClick={() => handleVerify(selectedReport.id)} disabled={verifying}
                  className="btn-primary flex items-center gap-2 bg-green-600 hover:bg-green-700">
                  {verifying ? (
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                  ) : (
                    <Shield className="w-4 h-4" />
                  )}
                  Verify Report
                </button>
              )}
              <button onClick={() => handlePrint(selectedReport.id)}
                className="btn-accent flex items-center gap-2">
                <Printer className="w-4 h-4" /> Print / PDF
              </button>
              <button onClick={() => setSelectedReport(null)} className="btn-secondary">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
